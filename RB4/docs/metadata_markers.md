# Metadata Markers

Song-specific metadata is embedded within the `.ark` files and can be identified by specific binary markers.

## RBSongMetadata

The marker `RBSongMetadata` indicates the start of a metadata block. These blocks contain key-value pairs describing song properties.

### Discovered Keys

The following keys have been located within `RBSongMetadata` blocks:

- `loaded_song_id`: The internal identifier for the song.
- `tempo`: The song's tempo.
- `vocal_tonic_note`: The tonic note for vocals.
- `vocal_track_scroll_duration_ms`: Duration for vocal track scrolling.
- `global_tuning_offset`: Tuning offset for the song.
- `band_fail_sound_event`: Sound event triggered on band failure.
- `vocal_percussion_patch`: Patch used for vocal percussion.
- `drum_kit_patch`: Patch used for drums.
- `improv_solo_patch`: Patch used for improvised solos.
- `dynamic_drum_fill_override`: Override for dynamic drum fills.
- `improv_solo_volume_db`: Volume adjustment for improvised solos.

### Value Storage

Values associated with these keys typically follow the same length-prefixed string pattern used throughout the `.ark` files.
