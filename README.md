Requirements:
```nix
(pkgs.texlive.combine {
  inherit (pkgs.texlive) scheme-medium
    musixtex
    musixtex-fonts
    songs;
})
```
