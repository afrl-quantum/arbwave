# vim: et:ts=2:sw=2:tw=80:nowrap
#
#       Py_Shell.py : inserts the python prompt in a gtk interface
#

import sys, code, os
import builtins


from gi.repository import Gtk as gtk, \
                          Gdk as gdk, \
                          GObject as gobject, \
                          Pango as pango, \
                          GLib as glib
import types, pydoc

textDoc = pydoc.TextDoc()
# no special bolding!
textDoc.bold = types.MethodType(lambda self,txt:txt, textDoc)

PS1=">>> "
PS2="... "
TAB_WIDTH=4

BANNER = \
  'Python ' + sys.version+ '\n'

FRAME_LABEL = \
  'Arbwave Command Line'




class Completer:
  """
  Taken from rlcompleter, with readline references stripped, and a local dictionary to use.
  """
  def __init__(self,locals):
    self.locals = locals

  def complete(self, text, state):
    """Return the next possible completion for 'text'.
    This is called successively with state == 0, 1, 2, ... until it
    returns None.  The completion should begin with 'text'.

    """
    if state == 0:
      if "." in text:
        self.matches = self.attr_matches(text)
      else:
        self.matches = self.global_matches(text)
    try:
      return self.matches[state]
    except IndexError:
      return None

  def global_matches(self, text):
    """Compute matches when text is a simple name.

    Return a list of all keywords, built-in functions and names
    currently defines in __main__ that match.

    """
    import keyword
    matches = []
    n = len(text)
    for list in [keyword.kwlist, builtins.__dict__.keys(), self.locals.keys()]:
      for word in list:
        if word[:n] == text and word != "builtins":
          matches.append(word)
    return matches

  def attr_matches(self, text):
    """Compute matches when text contains a dot.

    Assuming the text is of the form NAME.NAME....[NAME], and is
    evaluatable in the globals of __main__, it will be evaluated
    and its attributes (as revealed by dir()) are used as possible
    completions.  (For class instances, class members are are also
    considered.)

    WARNING: this can still invoke arbitrary C code, if an object
    with a __getattr__ hook is evaluated.

    """
    import re
    m = re.match(r"(\w+(\.\w+)*)\.(\w*)", text)
    if not m:
      return
    expr, attr = m.group(1, 3)
    object = eval(expr, self.locals, self.locals)
    words = dir(object)
    if hasattr(object,'__class__'):
      words.append('__class__')
      words = words + get_class_members(object.__class__)
    matches = []
    n = len(attr)
    for word in words:
      if word[:n] == attr and word != "builtins":
        matches.append("%s.%s" % (expr, word))
    return matches

def get_class_members(klass):
  ret = dir(klass)
  if hasattr(klass,'__bases__'):
     for base in klass.__bases__:
       ret = ret + get_class_members(base)
  return ret







class Dummy_File:
  def __init__(self, view, buffer, tag):
    """Implements a file-like object for redirect the stream to the buffer"""
    self.view = view
    self.buffer = buffer
    self.tag = tag

  def write(self, text):
    glib.idle_add( self._write, text )

  def _write(self, text):
    """Write text into the buffer and apply self.tag"""
    iter=self.buffer.get_end_iter()
    self.buffer.insert_with_tags(iter,text,self.tag)
    start,end = self.buffer.get_start_iter(), self.buffer.get_end_iter()
    self.buffer.apply_tag_by_name("no_edit",start,end)

    self.view.scroll_mark_onscreen(self.buffer.get_insert())

  def writelines(self, l):
    glib.idle_add( self._writelines, l )

  def _writelines(self, L):
    for l in L:
      self._write(l)

  def flush(self):
    pass

  def isatty(self):
    return 1



class PopUp:
  PAGE_SIZE = 8
  def __init__(self, text_view, list, position):
    self.text_view=text_view
    
    #avoid duplicate items in list
    tmp={}
    n_chars=0
    for item in list:
      dim=len(item)
      if dim>n_chars:
        n_chars=dim
      tmp[item]=None 
    list = sorted(tmp.keys())
    
    self.list=list
    self.position=position
    self.popup=gtk.Window(gtk.WindowType.POPUP)
    frame=gtk.Frame()
    sw=gtk.ScrolledWindow()
    sw.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.AUTOMATIC)
    model=gtk.ListStore(gobject.TYPE_STRING)
    for item in self.list:
       iter=model.append()
       model.set(iter, 0, item)

    self.list_view=gtk.TreeView(model)
    self.list_view.connect("row-activated", self.hide)
    self.list_view.set_property("headers-visible", False)
    selection=self.list_view.get_selection()
    selection.connect("changed",self.select_row)
    selection.select_path((0,))
    renderer=gtk.CellRendererText()
    column=gtk.TreeViewColumn("",renderer,text=0)
    self.list_view.append_column(column)
    sw.add(self.list_view)
    frame.add(sw)
    self.popup.add(frame)
    
    #set the width of the popup according with the length of the strings
    contest=self.popup.get_pango_context()
    desc=contest.get_font_description()
    lang=contest.get_language()
    metrics= contest.get_metrics(desc, lang)
    width= round(pango.units_to_double(metrics.get_approximate_char_width()* n_chars))
    if width>80:
      self.popup.set_size_request(width,200)
    else:
      self.popup.set_size_request(80,200)
    self.show_popup()


  def hide(self, *arg):
    self.popup.hide()
       
  def show_popup(self):
    buffer=self.text_view.get_buffer()
    iter=buffer.get_iter_at_mark(buffer.get_insert())
    
    rectangle=self.text_view.get_iter_location(iter)
    absX, absY=self.text_view.buffer_to_window_coords(gtk.TextWindowType.TEXT, 
                               rectangle.x+rectangle.width+20 ,
                               rectangle.y+rectangle.height+50)
    parent=self.text_view.get_parent()
    self.popup.move(self.position[0]+absX, self.position[1]+absY)
    self.popup.show_all()

           

  def prev(self, page=False):
    inc = int(page == False) or self.PAGE_SIZE

    sel = self.list_view.get_selection()
    model, iter = sel.get_selected()
    newIter = model.get_path(iter)
    if newIter != None and newIter[0] > 0:
      path = ( max(0, newIter[0]-inc), )
      self.list_view.set_cursor(path)
          

  def next(self, page=False):
    inc = int(page == False) or self.PAGE_SIZE

    sel = self.list_view.get_selection()
    model, iter = sel.get_selected()
    newIter = model.get_path(iter)
    mmax = len(model) -1
    if newIter != None and newIter[0] < mmax:
      path = ( min(mmax, newIter[0]+inc), )
      self.list_view.set_cursor(path)


  def sel_confirmed(self):
    sel = self.list_view.get_selection()
    self.select_row(sel)
    self.hide()

                                                                                                                                              
  def select_row(self, selection):
    model, iter= selection.get_selected()
    name=model.get_value(iter,0)
    buffer=self.text_view.get_buffer()
    end=buffer.get_iter_at_mark(buffer.get_insert())
    start=end.copy()
    start.backward_char()

    while start.get_char() not in " ,()[]":
      start.backward_char()

    start.forward_char()
    buffer.delete(start,end)
    iter=buffer.get_iter_at_mark(buffer.get_insert())
    buffer.insert(iter,name)


class NameDict(dict):
  def __init__(self, *a, **kw):
    dict.__init__(self,*a,**kw)
    self.__dict__ = self


class Python(gtk.Frame):
  def __init__( self,banner=BANNER,
                label_text=FRAME_LABEL,
                get_globals = lambda : dict(),
                reset = lambda **kw: None,
                ui = None ):
    super(Python, self).__init__()
    self.set_label = label_text

    self.remote_get_globals = get_globals
    self.remote_reset = reset
    self.ui = ui
    self._create_shell_cmds()
    self.banner=banner
    box=gtk.HBox()
    box.set_homogeneous(False)
    box.set_border_width(4)
    box.set_spacing(4)
    sw=gtk.ScrolledWindow()
    sw.set_policy(gtk.PolicyType.AUTOMATIC,gtk.PolicyType.AUTOMATIC)
    t_table=gtk.TextTagTable()
    # creates three tags
    tag_err=gtk.TextTag.new("error")
    tag_err.set_property("foreground","red")
    tag_err.set_property("font","monospace 10")
    t_table.add(tag_err)
    
    tag_out=gtk.TextTag.new("output")
    tag_out.set_property("foreground","blue")
    tag_out.set_property("font","monospace 10")
    t_table.add(tag_out)
    
    tag_in=gtk.TextTag.new("input")
    tag_in.set_property("foreground","black")
    tag_in.set_property("font","monospace 10")
    t_table.add(tag_in)

    tag_no_edit=gtk.TextTag.new("no_edit")
    tag_no_edit.set_property("editable",False)
    t_table.add(tag_no_edit)
    
    self.buffer=gtk.TextBuffer.new(t_table)
    #add the banner
    self.buffer.set_text(self.banner+PS1)
    start,end=self.buffer.get_bounds()
    self.buffer.apply_tag_by_name("output",start,end)
    self.buffer.apply_tag_by_name("no_edit",start,end)

    self.view=gtk.TextView()
    self.view.set_buffer(self.buffer)
    self.view.connect("key-press-event", self.key_press)
    self.view.connect("drag_data_received",self.drag_data_received)
    self.view.set_wrap_mode(gtk.WrapMode.CHAR)
    sw.add(self.view)
    box.pack_start(sw, True, True, 0)

    #creates  two dummy files
    self.dummy_out=Dummy_File(self.view, self.buffer, tag_out)
    self.dummy_err=Dummy_File(self.view, self.buffer, tag_err)

    #creates the console
    self.popup = None
    #create null history
    self.history      = [" "]
    self.history_pos  = 0

    self.kwargs = NameDict() # storage for persistent kwargs to reset(**)
    self.locals = NameDict()
    self.shell_store = NameDict(
      kwargs=self.kwargs,
      variables=self.locals,
    )
    # fake module trickery
    sys.modules['shell_store']            = self.shell_store
    sys.modules['shell_store.variables']  = self.shell_store.variables
    sys.modules['shell_store.kwargs']     = self.shell_store.kwargs

    self._reset(hard=2)
    
    self.show_all()
    self.add(box)




  def key_press(self, view, event):
    if self.popup!=None:
      # handle maneuvering inside the completion popup 
      if event.keyval == gdk.KEY_Up or \
         event.keyval == gdk.KEY_ISO_Left_Tab or \
        (event.keyval == gdk.KEY_p and event.state & gdk.ModifierType.CONTROL_MASK):
        self.popup.prev()
        return True 
      elif event.keyval == gdk.KEY_Page_Up:
        self.popup.prev(page=True)
        return True
      elif event.keyval == gdk.KEY_Down or \
           event.keyval == gdk.KEY_Tab or \
          (event.keyval == gdk.KEY_n and event.state & gdk.ModifierType.CONTROL_MASK):
        self.popup.next()
        return True 
      elif event.keyval == gdk.KEY_Page_Down:
        self.popup.next(page=True)
        return True
      elif event.keyval == gdk.KEY_Return:
        self.popup.sel_confirmed()
        self.popup=None
        return True 
      elif event.keyval in [ gdk.KEY_Control_L, gdk.KEY_Control_R,
                             gdk.KEY_Shift_L,   gdk.KEY_Shift_R,
                             gdk.KEY_Alt_L,     gdk.KEY_Alt_R ]:
        return False
      else:
        self.popup.hide()
        self.popup=None
    else:
      end=self.buffer.get_end_iter()
      start=self.buffer.get_iter_at_line(end.get_line())

      if event.keyval ==gdk.KEY_Up or \
        (event.keyval == gdk.KEY_p and event.state & gdk.ModifierType.CONTROL_MASK):
        # emacs style
        if self.history_pos>0:
          # remove text into the line...
          start.forward_chars(4)
          self.buffer.delete(start,end)
          #inset the new text
          pos=self.buffer.get_end_iter()
          self.buffer.insert(pos, self.history[self.history_pos])
          self.history_pos-=1
        else:
          gdk.beep()
        self.view.emit_stop_by_name("key-press-event")
        return True
        
      elif event.keyval ==gdk.KEY_Down or \
          (event.keyval == gdk.KEY_n and event.state & gdk.ModifierType.CONTROL_MASK):
        # emacs style
        if self.history_pos<len(self.history)-1:
          # remove text into the line...
          start.forward_chars(4)
          self.buffer.delete(start,end)
          #inset the new text
          pos=self.buffer.get_end_iter()
          self.history_pos+=1
          self.buffer.insert(pos, self.history[self.history_pos])

        else:
          gdk.beep()
        self.view.emit_stop_by_name("key-press-event")
        return True

      elif event.keyval ==gdk.KEY_f and event.state & gdk.ModifierType.CONTROL_MASK:
        # emacs style
        iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
        iter.forward_cursor_position()
        self.buffer.place_cursor(iter)
        return True

      elif event.keyval ==gdk.KEY_b and event.state & gdk.ModifierType.CONTROL_MASK:
        # emacs style
        iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
        iter.backward_cursor_position()
        if iter.editable(True):
          self.buffer.place_cursor(iter)
        return True

      elif event.keyval == gdk.KEY_Left:
        iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
        iter.backward_cursor_position()
        if not iter.editable(True):
          return True
        return False

      elif event.keyval == gdk.KEY_Home or \
          (event.keyval == gdk.KEY_a and
           event.state & gdk.ModifierType.CONTROL_MASK):
        # emacs style
        start,end=self.get_line_iters()
        self.buffer.place_cursor( start )
        return True

      elif event.keyval ==gdk.KEY_e and event.state & gdk.ModifierType.CONTROL_MASK:
        # emacs style
        start,end=self.get_line_iters()
        self.buffer.place_cursor( end )
        return True

      elif event.keyval == gdk.KEY_d and event.state & gdk.ModifierType.CONTROL_MASK:
        # emacs style
        iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
        next_iter = iter.copy()
        next_iter.forward_cursor_position()
        self.buffer.delete(iter, next_iter)
        return True

      elif event.keyval == gdk.KEY_u and event.state & gdk.ModifierType.CONTROL_MASK:
        # emacs style
        start,end=self.get_line_iters()
        iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
        self.buffer.delete(start, iter)
        return True

      elif event.keyval ==gdk.KEY_Tab:
        if not self.get_line().strip():
          iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
          self.buffer.insert(iter,TAB_WIDTH*" ")
        else:
          self.complete_text()
        return True

      elif event.keyval ==gdk.KEY_Return:
        command=self.get_line()
        self.exec_code(command)
        start,end=self.buffer.get_bounds()
        self.buffer.apply_tag_by_name("no_edit",start,end)
        self.buffer.place_cursor(end)

        return True

      elif event.keyval ==gdk.KEY_space and event.state & gdk.ModifierType.CONTROL_MASK:
        self.complete_text()
        return True
      
  
  def _create_shell_cmds(self):
    def reset( **kwargs ):
      """
      Rerun global script.

      Each of the keyword arguments will be passed into the global script in the
      global variable 'kwargs' (a python dictionary).
      """
      self.reset(True, False, kwargs=kwargs)

    def clear():
      """clear terminal output"""
      self.reset( hard=False, cmdline=True )

    def history():
      """show/clear(ie. history().clear()"""
      return self.history

    def store(**kwargs):
      """
      store an item(s) in the shell_store.variables module.
      This enables an item to be stored across terminal resets.
      Items stored in the shell_store module will be reloaded into the global
      environment after reset.
      Usage : store(name0=value0, name1=value1, ...)

      Direct access to these stored variables (e.g. to delete) can by done by:
      import shell_store.variables
      del shell_store.variables.name0
      """
      self.locals.update( **kwargs )

    def store_kwargs(**kwargs):
      """
      store a default keyword argument to the reset function in the shell_store
      module.  These items will automatically be added to reset(**kwargs) if not
      already specified explicity to reset(**kwargs).
      Usage : store(name0=value0, name1=value1, ...)

      Direct access to these stored variables (e.g. to delete) can by done by:
      import shell_store
      del shell_store.kwargs.name0
      """
      self.kwargs.update( **kwargs )

    def shell_help(*args, **kwargs):
      """help(object) for help about object"""
      if not (args or kwargs):
        fundoc = '\n'.join([ textDoc.docroutine(f) for f in self.shell_cmds ])
        print('  ArbWave Shell Help: \n',
              '  Some useful ArbWave commands: \n',
              fundoc)
        return
      help(*args, **kwargs)
    shell_help.__name__ = 'help'

    self.shell_cmds = [ reset, clear, history, store, store_kwargs, shell_help ]

    if self.ui:
      def save():
        """
        Save the configuration file.
        """
        self.ui.save()

      def saveas(target, keep=True):
        """
        target : target filename to save to
        keep   : whether to keep the current config filename after saving
                 [Default True]
        """
        old = self.ui.config_file
        self.ui.config_file = target
        try:
          self.ui.save()
        finally:
          self.ui.config_file = old


      self.shell_cmds += [ save, saveas, self.ui.quit ]


  def get_globals(self, G=None):
    if G is None:
      G = self.remote_get_globals()
    G.update(
      { f.__name__:f for f in self.shell_cmds },
      self=self,
      **self.locals
    )
    return G


  def update_globals(self, G=None):
    self.core.locals  = self.get_globals(G)
    #autocompletation capabilities
    self.completer    = Completer(self.core.locals)


  def reset(self, hard, cmdline=False, history=False, kwargs=dict()):
    glib.idle_add( self._reset, hard, cmdline, history, False, kwargs )

  def _reset(self, hard, cmdline=False, history=False, from_gui=False,
             kwargs=dict()):
    if hard:
      if int(hard) == 1:
        self.remote_reset( **dict(self.kwargs, **kwargs) )
      #creates the console
      self.core=code.InteractiveConsole()
      if history:
        #reset history
        self.history      = [" "]
        self.history_pos  = 0
      self.update_globals()
      if self.popup:
        self.popup.hide()
      self.popup = None

    if cmdline:
      if from_gui:
        self.buffer.set_text(PS1)
      else:
        self.buffer.set_text('')
      start,end=self.buffer.get_bounds()
      self.buffer.apply_tag_by_name("output",start,end)
      self.buffer.apply_tag_by_name("no_edit",start,end)

    self.view.grab_focus()


  def save_text(self, *widget):
    dlg=gtk.Dialog("Save to file")
    dlg.add_button("Commands",1)
    dlg.add_button("All",2)
    dlg.add_button(gtk.STOCK_CLOSE,gtk.ResponseType.CLOSE)
    dlg.set_default_size(250,150)
    hbox=gtk.HBox()
    #add an image
    img=gtk.Image()
    img.set_from_stock(gtk.STOCK_SAVE, gtk.IconSize.DIALOG)
    hbox.pack_start(img, True, True, 0)
    
    #add text
    text="You have two options:\n"
    text+="   -save only commands\n"
    text+="   -save all\n"
    text+="\n What do you want to save?"
    label=gtk.Label(text)
    hbox.pack_start(label, True, True, 0)
    
    hbox.show_all()
    dlg.vbox.pack_start(hbox, True, True, 0)
    
    ans=dlg.run()
    dlg.hide()
    if ans==1 :
      def ok_save(button, data=None):
        win =button.get_toplevel()
        win.hide()
        name=win.get_filename()
        if os.path.isfile(name):
          box=gtk.MessageDialog(dlg,
                            gtk.DialogFlags.DESTROY_WITH_PARENT,
                            gtk.MessageType.QUESTION,gtk.ButtonsType.YES_NO,
                          name+" already exists; do you want to overwrite it?"
                          )
          ans=box.run()
          box.hide()
          if ans==gtk.ResponseType.NO:
            return
        try:
          file=open(name,'w')
          for i in self.history:
            file.write(i)
            file.write("\n")
          file.close()
          
              
        except Exception as x:
          box=gtk.MessageDialog(dlg,
                            gtk.DialogFlags.DESTROY_WITH_PARENT,
                            gtk.MessageType.ERROR,gtk.ButtonsType.CLOSE,
                          "Unable to write \n"+
                          name+"\n on disk \n\n%s"%(x)
                          )
          box.run()
          box.hide()

      def cancel_button(button):
        win.get_toplevel()
        win.hide()
          
      win=gtk.FileSelection("Save Commands...")
      win.ok_button.connect_object("clicked", ok_save,win.ok_button)
      win.cancel_button.connect_object("clicked", cancel_button,win.cancel_button)
      win.show()
    elif ans==2:
      def ok_save(button, data=None):
        win =button.get_toplevel()
        win.hide()
        name=win.get_filename()
        if os.path.isfile(name):
          box=gtk.MessageDialog(dlg,
                            gtk.DialogFlags.DESTROY_WITH_PARENT,
                            gtk.MessageType.QUESTION,gtk.ButtonsType.YES_NO,
                          name+" already exists; do you want to overwrite it?"
                          )
          ans=box.run()
          box.hide()
          if ans==gtk.ResponseType.NO:
            return
        try:
          start,end=self.buffer.get_bounds()
          text=self.buffer.get_text(start,end,0)
          file=open(name,'w')
          file.write(text)
          file.close()
          
        except Exception as x:
          box=gtk.MessageDialog(dlg,
                            gtk.DialogFlags.DESTROY_WITH_PARENT,
                            gtk.MessageType.ERROR,gtk.ButtonsType.CLOSE,
                          "Unable to write \n"+
                          name+"\n on disk \n\n%s"%(x)
                          )
          box.run()
          box.hide()
          
      def cancel_button(button):
        win.get_toplevel()
        win.hide()
          
      win=gtk.FileSelection("Save Log...")
      win.ok_button.connect_object("clicked", ok_save,win.ok_button)
      win.cancel_button.connect_object("clicked", cancel_button,win.cancel_button)
      win.show()
    dlg.destroy()
    self.view.grab_focus()
      

  def get_line_iters(self):
    iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
    line=iter.get_line()
    start=self.buffer.get_iter_at_line(line)
    end=start.copy()
    end.forward_line()

    command=self.buffer.get_text(start,end,0)
    if   command.startswith(PS1):
      start.forward_chars( len(PS1) )
    elif command.startswith(PS2):
      start.forward_chars( len(PS2) )
    return start, end

        
  def get_line(self):
    start, end = self.get_line_iters()
    return self.buffer.get_text(start,end,0)


  def complete_text(self):
      end=self.buffer.get_iter_at_mark(self.buffer.get_insert())
      start=end.copy()
      start.backward_char()
      while start.get_char() not in " ,()[]=":
          start.backward_char()
      start.forward_char()
      token=self.buffer.get_text(start,end,0).strip() 
      completions = []
      try:
          p=self.completer.complete(token,len(completions))
          while p != None:
            completions.append(p)
            p=self.completer.complete(token, len(completions))
      except:
          return 
      if len(completions)==1:
          self.buffer.delete(start,end)
          iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
          self.buffer.insert(iter,completions[0])
      elif len(completions)>1:
          #show a popup 
          rect=self.get_allocation()
          app=self.get_window().get_root_origin()
          position=(app[0]+rect.x,app[1]+rect.y)

          self.popup=PopUp(self.view, completions, position) 

       
  def replace_line(self, text):
      iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
      line=iter.get_line()
      start=self.buffer.get_iter_at_line(line)
      start.forward_chars(4)
      end=start.copy()
      end.forward_line()
      self.buffer.delete(start,end)
      iter=self.buffer.get_iter_at_mark(self.buffer.get_insert())
      self.buffer.insert(iter, text)
      
      
                        
  def sdt2files(self):
      """switch stdin stdout stderr to my dummy files"""
      self.std_out_saved=sys.stdout
      self.std_err_saved=sys.stderr
      
      sys.stdout=self.dummy_out
      sys.stderr=self.dummy_err
      
      
      
      
      

  def files2sdt(self):
      """switch my dummy files to stdin stdout stderr  """
      sys.stdout=self.std_out_saved
      sys.stderr=self.std_err_saved
      



  def drag_data_received(self, source, drag_context, n1, n2, selection_data, long1, long2):
      print(selection_data.data)
      
      
  def exec_code(self, text):
      """Execute text into the console and display the output into TextView"""
      
      #update history
      self.history.append(text)
      self.history_pos=len(self.history)-1
      
      self.sdt2files()
      sys.stdout.write("\n")
      action=self.core.push(text)
      if action==0:
          sys.stdout.write(PS1)
      elif action==1:
          sys.stdout.write(PS2)
      self.files2sdt()



  def quit(self,*args):
      if __name__=='__main__':
          gtk.main_quit()
      else:
          if self.popup!=None:
              self.popup.hide()
          self.hide()








if __name__=='__main__':
  w = gtk.Window()
  w.set_default_size(520,200)
  shell=Python()
  w.add( shell )
  w.show_all()
  gtk.main()
