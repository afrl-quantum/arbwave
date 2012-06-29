# vim: ts=2:sw=2:tw=80:nowrap

def retlist( *args ):
  return args

def fixargs( args ):
  try:
    return retlist(*args)
  except:
    return [args]

class TreeModelDispatcher:
  """
  Simple signal aggregation for any changes to a single 'changed' signal.
  """
  def __init__( self, Model,
                changed=None,
                row_changed=None,
                row_deleted=None,
                row_inserted=None,
                rows_reordered=None ):
    self.Model = Model
    if changed:
      self.connect( 'changed', *fixargs(changed) )
    if row_changed:
      self.connect( 'row-changed', *fixargs(row_changed) )
    if row_deleted:
      self.connect( 'row-deleted', *fixargs(row_deleted) )
    if row_inserted:
      self.connect( 'row-inserted', *fixargs(row_inserted) )
    if rows_reordered:
      self.connect( 'rows-reordered', *fixargs(rows_reordered) )

  def connect(self, signal, callback, *args, **kwargs):
    if signal == 'changed':
      for i in [
        ('row-changed',    self.row_changed_cb   ),
        ('row-deleted',    self.row_deleted_cb   ),
        ('row-inserted',   self.row_inserted_cb  ),
        ('rows-reordered', self.rows_reordered_cb),
      ]:
        self.Model.connect(self, i[0],i[1], callback, *args, **kwargs )
    else:
      self.Model.connect(self, signal, callback, *args, **kwargs)

  def row_changed_cb(self, model, path, iter,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def row_deleted_cb(self, model, path,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def row_inserted_cb(self, model, path, iter,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)

  def rows_reordered_cb(self, model, path, iter, new_order,
                  callback, *args, **kwargs):
    callback(self, *args, **kwargs)
