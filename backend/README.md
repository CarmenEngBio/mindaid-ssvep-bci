# Cyton acquisition interface (real board or synthetic).
# Set USE_SYNTHETIC_BOARD = True in config.py to run without hardware 
#
# get_window()      -> non-destructive rolling view of the last WINDOW samples
#                      (used for classification). Async: if the board buffer is
#                      not yet full it waits for the missing samples.
#
# get_new_samples() -> DESTRUCTIVE read: drains the BrainFlow buffer and returns
#                      everything new since the last call (used for recording).