# go2rtc-nack

[go2rtc](https://github.com/AlexxIT/go2rtc) with one fix: its WebRTC sender
answers NACKs, so packets lost over UDP get retransmitted instead of freezing
the video until the next keyframe.

go2rtc registers pion's NACK responder but never reads RTCP from its
`RTPSender`s, so the responder never sees the browser's NACKs. `patch.py` starts
a reader goroutine for each sender track. Measured on the BlackDiamondHub
cameras page: stock go2rtc had heavy loss and freezes on UDP; the patched build
had essentially none.

## Image

```
ghcr.io/blackdiamondlodge/go2rtc-nack:latest
```

A drop-in replacement for `alexxit/go2rtc` (built with upstream's own
`docker/Dockerfile`, amd64 + arm64).

Tags:
- `latest`: newest upstream release, patched
- `vX.Y.Z`: that upstream release, patched
- `vX.Y.Z-nack-<sha>`: that release with this repo's patch at `<sha>`

## How it stays current

`.github/workflows/build.yml` runs daily. When upstream publishes a new release
it clones that tag, applies `patch.py`, builds, smoke-tests and pushes. If
upstream changes the code the patch hooks into, `patch.py` fails and the build
goes red rather than shipping an unpatched image. If upstream ships this same
fix, `patch.py` leaves the source alone.

Run it by hand from Actions, optionally with a specific upstream tag or
`force` to rebuild.
