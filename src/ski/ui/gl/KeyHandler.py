'''
  Module for handling key events within a PySki drawing window.
  Key functions are defined in an internal dictionary (key_map), matching
  keystroke symbol/modifier tuples to function names.
  Key handler functions should accept two arguments, a SkiGLConfig and
  SkiGLController.

  @author: Steve Roberts <steve.roberts@essarsoftware.co.uk>
  @version: 1.0 (3 Dec 2012)
'''

import logging as log
from math import sqrt

import pyglet.window.key as key

def __centre_on_last(cfg, ctl):
    #ctl.pan_centre(ctl.last_x - (cfg.window_width / 2), (cfg.window_height / 2) - ctl.last_y, 0.0)
    cx = (cfg.window_width - (2 * cfg.window_xmargin)) / 2
    cy = (cfg.window_height - (2 * cfg.window_ymargin)) / 2
    ctl.pan_view_to(cx - ctl.last_x, cy - ctl.last_y, 0)
    
def __pan_down(cfg, ctl):
    ctl.pan_view_down(cfg.pan_step_y / ctl.live_scale_y)

def __pan_left(cfg, ctl):
    ctl.pan_view_left(cfg.pan_step_x / ctl.live_scale_x)
    
def __pan_right(cfg, ctl):
    ctl.pan_view_right(cfg.pan_step_x / ctl.live_scale_x)
    
def __pan_up(cfg, ctl):
    ctl.pan_view_up(cfg.pan_step_y / ctl.live_scale_y)

def __play_pause_animation(cfg, ctl):
    if ctl.playing:
        ctl.animation_pause()
    else:
        ctl.animation_play()

def __reset(cfg, ctl):
    # Reset zoom factor
    ctl.zoom_view_reset()
    # Reset view
    ctl.pan_view_reset()

def __zoom_in(cfg, ctl):
    ctl.zoom_view_in(cfg.zoom_step)
    
def __zoom_in_small(cfg, ctl):
    ctl.zoom_view_in(sqrt(cfg.zoom_step))

def __zoom_out(cfg, ctl):
    ctl.zoom_view_out(cfg.zoom_step)
    
def __zoom_out_small(cfg, ctl):
    ctl.zoom_view_out(sqrt(cfg.zoom_step))

# Define a dictionary pairing key stroke values with handler functions
key_map = {
           (key.A, 0): __zoom_in
         , (key.A, key.MOD_SHIFT): __zoom_in_small
         , (key.C, 0): __centre_on_last
         , (key.Z, 0): __zoom_out
         , (key.Z, key.MOD_SHIFT): __zoom_out_small
         , (key._0, 0): __reset
         , (key.SPACE, 0): __play_pause_animation
         , (key.UP, 0): __pan_up
         , (key.UP, key.MOD_SHIFT): NotImplemented
         , (key.DOWN, 0): __pan_down
         , (key.DOWN, key.MOD_SHIFT): NotImplemented
         , (key.LEFT, 0): __pan_left
         , (key.RIGHT, 0): __pan_right
}

def key_str((symbol, modifiers)):
    return (key.symbol_string(symbol), key.modifiers_string(modifiers))
    

def handle_key_press(symbol, modifiers, cfg, ctl):
    '''
      Main keystroke handing function.  Checks defined key handlers in a dict
      to find and execute defined functions.
      @param symbol: the pressed key symbol
      @param modifiers: the pressed key modifiers
      @param cfg: the current GL configuration
      @param ctl: the current GL controller
    '''
    k = (symbol, modifiers)
    log.debug('[KeyHandler] Key press %s trapped', key_str(k))
    if k in key_map:
        # Key handler function from dict
        f = key_map[k]
        log.debug('[KeyHandler] Key handler found: %s', f)
        
        if f is NotImplemented:
            log.warn('[KeyHandler] Handler is %s for %s', f, key_str(k))
        else:
            # Wrap in a try/except block to prevent bad handler functions
            # from crashing entire app
            try:
                key_map[k](cfg, ctl)
            except:
                # Log error details
                log.exception('[KeyHandler] Error executing key handler %s for %s', f.__name__, key_str(k))
                # Exit method
                return