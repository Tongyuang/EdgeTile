# kvazaar
An open-source HEVC encoder
## encoding priority format
`array_len,-priority1,tile1,tile2,-priority2,tile3,tile4`

# modification:
  - support tile encoding priority: add `tiles_encoding_priority` to `kvz_config` and pass the encoder to `threadqueue_queue_t`, when a ready job is push into the `threadqueue_queue_t`, insert it according to its priority``
  ```c
  kvz_encoder* encoder = threadqueue->encoder;
  int32_t* priority_arr = encoder->control->cfg.tiles_encoding_priority;
  for (int i = 0; priority_arr[i] >= 0; i++) {
	  if (priority_arr[i] == tile_id) {
		  state->encoding_priority = 1;
	  }
  }
  ```
  
  - output tile nals once encoded: pass a callback function ` void(*stream_callback_fptr)(int tile_id, void *chunk_data)` to `encoder_control_t` and the function will be called in the write-stream jobs: 
  (1)`kvz_encoder_state_worker_parameters_bitstream` to write vps, pps, sps. 
  (2) `kvz_encoder_state_worker_slice_bitstream` to write slice nals.
  (3) `kvz_encoder_state_worker_finish_frame_bitstream` does nothing but tells the encoder the whole frame has been output. The order is contrained by 
  ```c
  kvz_threadqueue_job_dep_add(slice_job, parameter_set_job);
  kvz_threadqueue_job_dep_add(finish_job, slice_job);
  ```
  which can be find in encoderstate.c `kvz_encode_one_frame`
  
  - support each tile can be decoded. set `first_slice_segment_in_pic` and `slice_segment_address` and modify `openHEVC` to decode each tile stream.
  
