Requirements:
```nix
(pkgs.texlive.combine {
  inherit (pkgs.texlive) scheme-medium
    musixtex
    musixtex-fonts
    songs;
})
```

Chords from: <https://github.com/T-vK/chord-collection>

Tab download is done with [ugd](https://git.sr.ht/~tarneo/ugd).
