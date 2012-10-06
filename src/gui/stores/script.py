# vim: ts=2:sw=2:tw=80:nowrap

from .. import edit

class Undo:
  """Script Undo class"""
  def __init__(self, old_text, new_text, script):
    self.old_text = old_text
    self.new_text = new_text
    self.script = script

  def undo(self):
    self.script.set_text( self.old_text, skip_undo=True )
    self.script.edit() # show the editor

  def redo(self):
    self.script.set_text( self.new_text, skip_undo=True )
    self.script.edit() # show the editor


class Script:
  def __init__( self, text='', title='Script', parent=None,
                add_undo=None,
                changed=None, *changed_args, **changed_kwargs ):
    self.editor   = None
    self.text     = text
    self.title    = title
    self.parent   = parent
    self.add_undo = add_undo
    self.onchange = None

    if changed:
      self.connect( 'changed', changed, *changed_args, **changed_kwargs )

  def __str__(self):
    return self.text

  def clear(self):
    self.set_text('')

  def set_text(self, t, skip_undo=False):
    if not ( skip_undo or self.add_undo is None ):
      self.add_undo( Undo(self.text, t, self) )

    self.text = t
    if self.editor:
      self.editor.set_text( t )
    if self.onchange:
      self.onchange['callable'](
        self, *self.onchange['args'], **self.onchange['kwargs']
      )

  def get_text(self):
    return self.text

  def load(self, t):
    self.set_text(t)

  def representation(self):
    return str(self)

  def connect(self, signal, callback, *args, **kwargs):
    if signal == 'changed':
      self.onchange = {
        'callable'  : callback,
        'args'      : args,
        'kwargs'    : kwargs,
      }
    else:
      raise TypeError('unkown signal ' + signal)

  def edit(self):

    def unset_editor(*args):
      print 'unsettling'
      self.editor = None

    if not self.editor:
      self.editor = edit.script.Editor( self.title, self.parent, target=self )
      self.editor.connect('delete-event', self.editor.hide_on_delete)
      self.editor.connect('destroy', unset_editor)

    self.editor.present()

