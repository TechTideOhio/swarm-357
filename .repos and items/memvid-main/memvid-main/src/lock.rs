use std::fs::{File, OpenOptions};
use std::path::Path;
use std::thread;
use std::time::Duration;

use fs2::FileExt;

use crate::error::{MemvidError, Result};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LockMode {
    None,
    Shared,
    Exclusive,
}

/// File lock guard that can hold either a shared or exclusive OS lock.
pub struct FileLock {
    file: File,
    mode: LockMode,
}

impl FileLock {
    /// Opens a file at `path` with read/write permissions and acquires an exclusive lock.
    pub fn open_and_lock(path: &Path) -> Result<(File, Self)> {
        let file = OpenOptions::new().read(true).write(true).open(path)?;
        let guard = Self::acquire_with_mode(&file, LockMode::Exclusive)?;
        Ok((file, guard))
    }

    /// Opens a file at `path` with read/write permissions and acquires a shared lock.
    pub fn open_read_only(path: &Path) -> Result<(File, Self)> {
        let file = OpenOptions::new().read(true).write(true).open(path)?;
        let guard = Self::acquire_with_mode(&file, LockMode::Shared)?;
        Ok((file, guard))
    }

    /// Returns a non-locking guard for callers that only require a stable clone handle.
    pub fn unlocked(file: &File) -> Result<Self> {
        Ok(Self {
            file: file.try_clone()?,
            mode: LockMode::None,
        })
    }

    /// Clones the provided file handle and locks it exclusively.
    pub fn acquire(file: &File, _path: &Path) -> Result<Self> {
        Self::acquire_with_mode(file, LockMode::Exclusive)
    }

    /// Attempts a non-blocking exclusive lock, returning None if already locked.
    pub fn try_acquire(_file: &File, path: &Path) -> Result<Option<Self>> {
        let clone = OpenOptions::new().read(true).write(true).open(path)?;
        loop {
            match clone.try_lock_exclusive() {
                Ok(()) => {
                    return Ok(Some(Self {
                        file: clone,
                        mode: LockMode::Exclusive,
                    }));
                }
                Err(err) if err.kind() == std::io::ErrorKind::Interrupted => continue,
                Err(err) if err.kind() == std::io::ErrorKind::WouldBlock => return Ok(None),
                Err(err) => return Err(MemvidError::Lock(err.to_string())),
            }
        }
    }

    /// Releases the underlying OS file lock.
    pub fn unlock(&mut self) -> Result<()> {
        if self.mode == LockMode::None {
            return Ok(());
        }
        self.file
            .unlock()
            .map_err(|err| MemvidError::Lock(err.to_string()))
    }

    /// Exposes a clone of the locked handle for buffered operations.
    pub fn clone_handle(&self) -> Result<File> {
        Ok(self.file.try_clone()?)
    }

    #[must_use]
    pub fn mode(&self) -> LockMode {
        self.mode
    }

    pub fn downgrade_to_shared(&mut self) -> Result<()> {
        if self.mode == LockMode::None {
            return Err(MemvidError::Lock(
                "cannot downgrade an unlocked file handle".to_string(),
            ));
        }
        if self.mode == LockMode::Shared {
            return Ok(());
        }
        self.file
            .unlock()
            .map_err(|err| MemvidError::Lock(err.to_string()))?;
        Self::lock_with_retry(&self.file, LockMode::Shared)?;
        self.mode = LockMode::Shared;
        Ok(())
    }

    pub fn upgrade_to_exclusive(&mut self) -> Result<()> {
        if self.mode == LockMode::None {
            return Err(MemvidError::Lock(
                "cannot upgrade an unlocked file handle".to_string(),
            ));
        }
        if self.mode == LockMode::Exclusive {
            return Ok(());
        }
        self.file
            .unlock()
            .map_err(|err| MemvidError::Lock(err.to_string()))?;
        Self::lock_with_retry(&self.file, LockMode::Exclusive)?;
        self.mode = LockMode::Exclusive;
        Ok(())
    }

    pub(crate) fn acquire_with_mode(file: &File, mode: LockMode) -> Result<Self> {
        let clone = file.try_clone()?;
        Self::lock_with_retry(&clone, mode)?;
        Ok(Self { file: clone, mode })
    }

    fn lock_with_retry(file: &File, mode: LockMode) -> Result<()> {
        const MAX_ATTEMPTS: u32 = 200; // ~10 seconds with 50ms backoff
        const BACKOFF: Duration = Duration::from_millis(50);
        let mut attempts = 0;
        loop {
            let result = match mode {
                LockMode::None => return Ok(()),
                LockMode::Exclusive => file.try_lock_exclusive(),
                LockMode::Shared => FileExt::try_lock_shared(file),
            };
            match result {
                Ok(()) => return Ok(()),
                Err(err) if err.kind() == std::io::ErrorKind::Interrupted => continue,
                Err(err) if err.kind() == std::io::ErrorKind::WouldBlock => {
                    if attempts >= MAX_ATTEMPTS {
                        return Err(MemvidError::Lock(
                            "exclusive access unavailable; file is in use by another process"
                                .to_string(),
                        ));
                    }
                    attempts += 1;
                    thread::sleep(BACKOFF);
                    continue;
                }
                Err(err) => return Err(MemvidError::Lock(err.to_string())),
            }
        }
    }
}

impl Drop for FileLock {
    fn drop(&mut self) {
        if self.mode != LockMode::None {
            let _ = self.file.unlock();
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    #[cfg(not(target_os = "windows"))] // Windows has different file locking semantics
    fn acquiring_lock_blocks_second_writer() {
        let temp = NamedTempFile::new().expect("temp file");
        let path = temp.path();
        writeln!(&mut temp.as_file().try_clone().unwrap(), "seed").unwrap();

        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .open(path)
            .expect("open file");
        let guard = FileLock::acquire(&file, path).expect("first lock succeeds");

        let second = FileLock::try_acquire(&file, path).expect("second lock attempt");
        assert!(second.is_none(), "lock should already be held");

        drop(guard);
        let third = FileLock::try_acquire(&file, path).expect("third lock attempt");
        assert!(third.is_some(), "lock released after drop");
    }
}
