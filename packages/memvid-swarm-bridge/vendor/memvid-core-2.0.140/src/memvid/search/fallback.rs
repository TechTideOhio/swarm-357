#![cfg(feature = "lex")]

#[cfg(feature = "temporal_track")]
use super::helpers::attach_temporal_metadata;
use super::helpers::{build_context, empty_search_response, parse_cursor, timestamp_to_rfc3339};
use crate::lex::{LexMatch, compute_snippet_slices};
use crate::memvid::lifecycle::Memvid;
use crate::search::{EvaluationContext, ParsedQuery};
use crate::types::{
    Frame, FrameId, SearchEngineKind, SearchHit, SearchHitMetadata, SearchParams, SearchRequest,
    SearchResponse,
};
use crate::{MemvidError, Result};
use std::collections::HashSet;
use std::time::Instant;

pub(super) fn search_with_lex_fallback(
    memvid: &mut Memvid,
    parsed: &ParsedQuery,
    query_tokens: &[String],
    request: &SearchRequest,
    params: &SearchParams,
    start_time: Instant,
    candidate_filter: Option<&HashSet<FrameId>>,
) -> Result<SearchResponse> {
    let index = memvid
        .lex_index
        .as_ref()
        .ok_or(MemvidError::LexNotEnabled)?;
    let uri_filter = request.uri.as_deref();
    let scope_filter = if uri_filter.is_some() {
        None
    } else {
        request.scope.as_deref()
    };

    let matches: Vec<LexMatch> = index.compute_matches(query_tokens, uri_filter, scope_filter);
    let snippet_window = request.snippet_chars.max(80);
    let max_snippets_per_doc = request.top_k.max(1);

    let mut evaluated = Vec::new();
    let mut stale_skips = 0u32;
    for matched in &matches {
        if let Some(filter) = candidate_filter {
            if !filter.contains(&matched.frame_id) {
                continue;
            }
        }
        let Some(frame_meta) = usize::try_from(matched.frame_id)
            .ok()
            .and_then(|idx| memvid.toc.frames.get(idx))
        else {
            tracing::warn!(
                frame_id = matched.frame_id,
                "skipping search hit with stale frame_id"
            );
            stale_skips = stale_skips.saturating_add(1);
            continue;
        };
        let content_lower = matched.content.to_ascii_lowercase();
        let ctx = EvaluationContext {
            frame: frame_meta,
            content_lower: &content_lower,
        };
        if !parsed.evaluate(&ctx) {
            continue;
        }

        let slices = compute_snippet_slices(
            &matched.content,
            &matched.occurrences,
            snippet_window,
            max_snippets_per_doc,
        );
        evaluated.push((matched, slices));
    }

    let total_slices: usize = evaluated.iter().map(|(_, slices)| slices.len()).sum();
    if total_slices == 0 {
        let elapsed_ms = start_time.elapsed().as_millis();
        return Ok(empty_search_response(
            request.query.clone(),
            params.clone(),
            elapsed_ms,
            SearchEngineKind::LexFallback,
        ));
    }

    let offset = parse_cursor(request.cursor.as_deref(), total_slices)?;
    let effective_top_k = request.top_k.max(1);

    let mut hits = Vec::new();
    let mut produced = 0usize;
    for (matched, slices) in evaluated {
        let Some(frame_meta) = memvid
            .toc
            .frames
            .get(usize::try_from(matched.frame_id).unwrap_or(usize::MAX))
            .cloned()
        else {
            tracing::warn!(
                frame_id = matched.frame_id,
                "skipping stale frame_id in snippet assembly"
            );
            continue;
        };
        let canonical = memvid.frame_content(&frame_meta)?;
        let canonical_limit = frame_meta.canonical_length.map_or_else(
            || canonical.len(),
            |len| {
                // Safe: canonical length is reasonably small string length
                #[allow(clippy::cast_possible_truncation)]
                let l = len as usize;
                l
            },
        );
        let canonical_len = canonical.len();
        let effective_len = canonical_limit.min(canonical_len);
        let uri = matched
            .uri
            .clone()
            .or_else(|| frame_meta.uri.clone())
            .unwrap_or_else(|| crate::default_uri(matched.frame_id));
        let title = matched
            .title
            .clone()
            .or_else(|| frame_meta.title.clone())
            .or_else(|| crate::infer_title_from_uri(&uri));

        for (start, end) in slices {
            if produced < offset {
                produced += 1;
                continue;
            }
            if hits.len() == effective_top_k {
                break;
            }

            let matches_in_slice = matched
                .occurrences
                .iter()
                .filter(|(s, e)| *s >= start && *e <= end)
                .count()
                .max(1);
            let metadata = SearchHitMetadata {
                matches: matches_in_slice,
                tags: frame_meta.tags.clone(),
                labels: frame_meta.labels.clone(),
                track: frame_meta.track.clone(),
                created_at: timestamp_to_rfc3339(frame_meta.timestamp),
                content_dates: frame_meta.content_dates.clone(),
                entities: Vec::new(),
                extra_metadata: frame_meta.extra_metadata.clone(),
                #[cfg(feature = "temporal_track")]
                temporal: None,
            };

            let chunk_start = matched.chunk_offset;
            let chunk_end = (chunk_start + matched.content.len()).min(effective_len);
            if chunk_end <= chunk_start {
                produced += 1;
                continue;
            }
            let chunk_range = (chunk_start, chunk_end);
            let global_start = (chunk_start + start).min(chunk_end);
            let global_end = (chunk_start + end).min(chunk_end);
            if global_end <= global_start {
                produced += 1;
                continue;
            }
            let canonical_bytes = canonical.as_bytes();
            let snippet_text =
                String::from_utf8_lossy(&canonical_bytes[global_start..global_end]).to_string();
            let chunk_text =
                String::from_utf8_lossy(&canonical_bytes[chunk_start..chunk_end]).to_string();
            hits.push(SearchHit {
                rank: hits.len() + 1,
                frame_id: matched.frame_id,
                uri: uri.clone(),
                title: title.clone(),
                range: (global_start, global_end),
                text: snippet_text,
                matches: matches_in_slice,
                chunk_range: Some(chunk_range),
                chunk_text: Some(chunk_text),
                score: Some(matched.score),
                metadata: Some(metadata),
            });
            produced += 1;
        }
    }

    let next_cursor = if produced < total_slices {
        Some(produced.to_string())
    } else {
        None
    };

    let elapsed_ms = start_time.elapsed().as_millis().max(1);
    #[cfg(feature = "temporal_track")]
    attach_temporal_metadata(memvid, &mut hits)?;
    let context = build_context(&hits);

    Ok(SearchResponse {
        query: request.query.clone(),
        elapsed_ms,
        total_hits: total_slices,
        params: params.clone(),
        hits,
        context,
        next_cursor,
        engine: SearchEngineKind::LexFallback,
        stale_index_skips: stale_skips,
    })
}

pub(super) fn search_with_filters_only(
    memvid: &mut Memvid,
    parsed: &ParsedQuery,
    request: &SearchRequest,
    params: &SearchParams,
    start_time: Instant,
    candidate_filter: Option<&HashSet<FrameId>>,
) -> Result<SearchResponse> {
    let mut matches = Vec::new();
    let snippet_limit = request.snippet_chars.max(80);
    let frames: Vec<Frame> = if let Some(filter) = candidate_filter {
        memvid
            .toc
            .frames
            .iter()
            .filter(|frame| filter.contains(&frame.id))
            .cloned()
            .collect()
    } else {
        memvid.toc.frames.clone()
    };

    for frame in frames {
        let search_text = memvid.frame_search_text(&frame)?;
        let content_lower = search_text.to_ascii_lowercase();
        let ctx = EvaluationContext {
            frame: &frame,
            content_lower: &content_lower,
        };
        if !parsed.evaluate(&ctx) {
            continue;
        }
        matches.push((frame.id, frame, search_text));
    }

    let total_hits = matches.len();
    if total_hits == 0 {
        let elapsed_ms = start_time.elapsed().as_millis().max(1);
        return Ok(SearchResponse {
            query: request.query.clone(),
            elapsed_ms,
            total_hits,
            params: params.clone(),
            hits: Vec::new(),
            context: build_context(&[]),
            next_cursor: None,
            engine: SearchEngineKind::LexFallback,
            stale_index_skips: 0,
        });
    }

    let offset = parse_cursor(request.cursor.as_deref(), total_hits)?;
    let effective_top_k = request.top_k.max(1);
    let mut hits = Vec::new();
    let mut produced = 0usize;

    for (frame_id, frame, search_text) in matches.into_iter().skip(offset) {
        if hits.len() == effective_top_k {
            break;
        }
        let snippet: String = search_text.chars().take(snippet_limit).collect();
        let snippet_bytes = snippet.len();
        let metadata = SearchHitMetadata {
            matches: 1,
            tags: frame.tags.clone(),
            labels: frame.labels.clone(),
            track: frame.track.clone(),
            created_at: timestamp_to_rfc3339(frame.timestamp),
            content_dates: frame.content_dates.clone(),
            entities: Vec::new(),
            extra_metadata: frame.extra_metadata.clone(),
            #[cfg(feature = "temporal_track")]
            temporal: None,
        };

        let uri = frame
            .uri
            .clone()
            .unwrap_or_else(|| crate::default_uri(frame_id));
        let title = frame
            .title
            .clone()
            .or_else(|| crate::infer_title_from_uri(&uri));

        hits.push(SearchHit {
            rank: hits.len() + 1,
            frame_id,
            uri,
            title,
            range: (0, snippet_bytes),
            text: snippet.clone(),
            matches: 1,
            chunk_range: Some((0, snippet_bytes)),
            chunk_text: Some(snippet),
            score: None,
            metadata: Some(metadata),
        });
        produced += 1;
    }

    let next_cursor = if offset + produced < total_hits {
        Some((offset + produced).to_string())
    } else {
        None
    };

    let elapsed_ms = start_time.elapsed().as_millis().max(1);
    #[cfg(feature = "temporal_track")]
    attach_temporal_metadata(memvid, &mut hits)?;
    let context = build_context(&hits);

    Ok(SearchResponse {
        query: request.query.clone(),
        elapsed_ms,
        total_hits,
        params: params.clone(),
        hits,
        context,
        next_cursor,
        engine: SearchEngineKind::LexFallback,
        stale_index_skips: 0,
    })
}
