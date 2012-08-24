% (c) 2006 Jose Luis Diaz and Spencer. E. Olson.
% This BST file is NOT for creating list of symbols or glossaries.  It is for
% using the infrastructure of the gloss package to lookup words and
% symbols stored in a bibtex database.  This is very useful in creating
% consistency throughout a large document that uses many mathematical symbols. 
% Rather than type out each symbol every time, just refer to the item stored
% in the database.  If you want to change the look of a particular symbol,
% just change the database and all instances in the document automatically
% match.  
%
% All Rights Reserved.
%

STRINGS { s t }

ENTRY
  { word
    sort-word
    definition
    heading
    group
    short
	sort-short
  }
  {}
  { ucword }
  
FUNCTION {not}
{   { #0 }
    { #1 }
  if$
}

FUNCTION {str.length}
{ 't :=
  #0
    { t empty$ not }
    { t #2 global.max$ substring$
	  't :=
	  #1 +
    }
  while$
}


FUNCTION {upper.first}
{ duplicate$
  #1 text.prefix$
  duplicate$
  "u" change.case$
  's :=
  str.length
  #1 + entry.max$ substring$
  s swap$ *
}

FUNCTION {check.required}
{ 's :=
  duplicate$ empty$
    { "Empty " s * " in " * cite$ * warning$ }
    'skip$
  if$
}

FUNCTION {field.or.null}
{ duplicate$ empty$
    { pop$ "" }
    'skip$
  if$
}

FUNCTION {push.sortword}
{ sort-word empty$ 
   { word field.or.null }
   'sort-word
  if$
}

FUNCTION {check.alpha}
{ duplicate$
  purify$
  empty$
    { "Non alphabetical " cite$ *
      " entry without group field" * warning$ }
    'skip$
  if$
}

FUNCTION {push.heading}
{ heading empty$
    { word field.or.null
      #1 text.prefix$
      check.alpha
    }
    'heading
    if$
}

FUNCTION {create.glossitem}
{ newline$
  "\lookupitem{" write$
  cite$ write$
  "}{" write$
  word write$
  "}{" write$
  ucword write$
  "}{" write$
  short field.or.null write$
  "}{" write$
  definition field.or.null write$
  "}" write$
  newline$
}

FUNCTION {create.symbol}
{ newline$
  "\lookupitem{" write$
  cite$ write$
  "}{\ensuremath{" write$
  word write$
  "}}{\ensuremath{" write$
  word write$
  "}}{" write$
  short field.or.null write$
  "}{" write$
  definition field.or.null write$
  "}" write$
  newline$
}



FUNCTION {set.vars}
{ word field.or.null
  "word" check.required
  upper.first
  'ucword := 
}


FUNCTION {glossdef}
{
  create.glossitem      % this outputs word, ucword, short, and def
}

FUNCTION {gd} { glossdef }


FUNCTION {symbdef}
{
  create.symbol         % this outputs $word$, $word$, short, and def
}

FUNCTION {symb} { symbdef }
FUNCTION {symbol} { symbdef }

FUNCTION {default.type} { glossdef }

FUNCTION {presort}
{ set.vars
  push.sortword
  group empty$
    { purify$ "L" }
    'group
  if$                    % sort-word heading
  swap$ *                % heading * sort-word
  "l" change.case$
  'sort.key$ :=
}

FUNCTION {call.entries}
  { call.type$
  }

READ

ITERATE {presort}

SORT

ITERATE {call.entries}

