
# EdgeTileClient

## Config

some options that config.yaml can support:
```yaml
client: 
	encoder:
		mode: # ['LOCAL_FILE_MODE', 'SERVER_MODE'].In "LOCAL_FILE_MODE", we can test the kcfcpp_tracker without server.
	tracker:
		select_model: # ['kcfcpp_tracker', 'glimpse_tracker', 'opencv_tracker', 'dat_tracker', 'optical_flow']
		insert_frame: # int type, set the number of selected frames, 0 means selecting no frames from cache.
		zoom_scale: # int type, can resize the frame, 1 is the same size as the raw_frame, 2 is the 1/2 size of the raw_frame.
		opencv_tracker:
			tracker: # ['BOOSTING', 'MIL', 'TLD', 'CSRT'], not useful
```
## DAT tracker
https://github.com/foolwood/DAT
## KCFCPP tracker
https://github.com/joaofaro/KCFcpp