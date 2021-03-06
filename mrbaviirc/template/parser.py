""" A parser for the template engine. """

__author__      = "Brian Allen Vanderburg II"
__copyright__   = "Copyright 2016"
__license__     = "Apache License 2.0"


import re


from .errors import *
from .nodes import *
from .expr import *
from .scope import *


class Token(object):
    """ Represent a token. """
    TYPE_TEXT           = 1
    TYPE_START_COMMENT  = 2
    TYPE_END_COMMENT    = 3
    TYPE_START_ACTION   = 4
    TYPE_END_ACTION     = 5
    TYPE_START_EMITTER  = 6
    TYPE_END_EMITTER    = 7
    TYPE_STRING         = 8
    TYPE_INTEGER        = 9
    TYPE_FLOAT          = 10
    TYPE_START_LIST     = 11
    TYPE_END_LIST       = 12
    TYPE_START_FUNC     = 13
    TYPE_END_FUNC       = 14
    TYPE_COMMA          = 15
    TYPE_EQUAL          = 16
    TYPE_WORD           = 17

    WS_NONE = 0
    WS_TRIMTONL = 1
    WS_TRIMTONL_PRESERVENL = 2
    WS_ADDNL = 3
    WS_ADDSP = 4

    def __init__(self, type, line, value=None):
        """ Initialize a token. """
        self._type = type
        self._line = line
        self._value = value


class Tokenizer(object):
    """ Parse text into some tokens. """
    MODE_TEXT       = 1
    MODE_COMMENT    = 2
    MODE_OTHER      = 3

    _alpha = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    _digit = "0123456789"

    _symbol_map = {
        "[": Token.TYPE_START_LIST,
        "]": Token.TYPE_END_LIST,
        "(": Token.TYPE_START_FUNC,
        ")": Token.TYPE_END_FUNC,
        ",": Token.TYPE_COMMA,
        "=": Token.TYPE_EQUAL
    }

    _tag_map = {
        "{#": Token.TYPE_START_COMMENT,
        "{%": Token.TYPE_START_ACTION,
        "{{": Token.TYPE_START_EMITTER,
        "#}": Token.TYPE_END_COMMENT,
        "%}": Token.TYPE_END_ACTION,
        "}}": Token.TYPE_END_EMITTER
    }

    _ws_map = {
        "-": Token.WS_TRIMTONL,
        "^": Token.WS_TRIMTONL_PRESERVENL,
        "+": Token.WS_ADDNL,
        "*": Token.WS_ADDSP
    }

    def __init__(self, text, filename):
        """ Initialze the tokenizer. """
        self._text = text
        self._filename = filename
        self._line = 1
        self._mode = self.MODE_TEXT
        self._tokens = []

    def parse(self):
        """ Parse the tokens and return the sequence. """

        self._mode = self.MODE_TEXT
        pos = 0

        while pos < len(self._text):
            if self._mode == self.MODE_TEXT:
                pos = self._parse_mode_text(pos)

            elif self._mode == self.MODE_COMMENT:
                pos = self._parse_mode_comment(pos)

            else:
                pos = self._parse_mode_other(pos)

        return self._tokens


    def _parse_mode_text(self, start):
        """ Parse while in text mode. """
        # Search for open block. If not a tag, pass through as a normal block.
        # Makes text containing { and } easier. To pass litteral {{, {#, or {%,
        # use {{ "{{" }} in the template
        pos = start
        while True:
            pos = self._text.find("{", pos)
            if pos == -1:
                break

            tag = self._text[pos:pos + 2]

            if tag in self._tag_map:
                break
                
            pos += 2
            continue

        # Add any preceeding text
        if pos == -1:
            block = self._text[start:]
        else:
            block = self._text[start:pos]

        if block:
            token = Token(Token.TYPE_TEXT, self._line, block)
            self._tokens.append(token)
            self._line += block.count("\n")

        if pos == -1:
            # No more tags
            return len(self._text)

        # Get whitespace control
        wscontrol = self._ws_map.get(self._text[pos + 2:pos + 3], Token.WS_NONE)

        # Create token
        type = self._tag_map[tag]
        token = Token(type, self._line, wscontrol)
        self._tokens.append(token)
        if type == Token.TYPE_START_COMMENT:
            self._mode = self.MODE_COMMENT
        else:
            self._mode = self.MODE_OTHER

        # Return next position
        if wscontrol != Token.WS_NONE:
            return pos + 3
        else:
            return pos + 2

    def _parse_mode_comment(self, start):
        """ Parse a comment tag. """

        # Just look for the ending
        pos = self._text.find("#}", start)

        if pos == -1:
            # No more tokens
            self._line += self._text[start:].count("\n")
            self._mode = self.MODE_TEXT
            return len(self._text)

        else:
            wscontrol = self._ws_map.get(self._text[pos - 1], Token.WS_NONE)

            self._line += self._text[start:pos].count("\n")
            token = Token(Token.TYPE_END_COMMENT, self._line, wscontrol)

            self._tokens.append(token)
            self._mode = self.MODE_TEXT
            return pos + 2

    def _parse_mode_other(self, start):
        """ Parse other stuff. """

        pos = start
        while pos < len(self._text):
            ch = self._text[pos]

            # Whitespace is ignored
            if ch in (" ", "\t", "\n"):
                if ch == "\n":
                    self._line += 1

                pos += 1
                continue

            # Single symbols
            if ch in self._symbol_map:
                token = Token(self._symbol_map[ch], self._line)
                self._tokens.append(token)

                pos += 1
                continue

            # Number
            if ch in self._digit:
                pos = self._parse_number(pos)
                continue

            # String
            if ch == "\"":
                pos = self._parse_string(pos)
                continue

            # A word value:
            if ch in self._alpha or ch == "_":
                pos = self._parse_word(pos)
                continue

            # Ending tag
            if ch in ("-", "^", "+", "*", "%", "#", "}"):

                # Check for number first if starts with "-" or "+"
                if ch in ("-", "+") and self._text[pos + 1:pos + 2] in self._digit:
                    pos = self._parse_number(pos)
                    continue

                wscontrol = self._ws_map.get(ch, Token.WS_NONE)
                if wscontrol != Token.WS_NONE:
                    pos += 1

                tag = self._text[pos:pos + 2]
                if not tag in ("#}", "%}", "}}"):
                    raise SyntaxError(
                        "Invalid tag: {0}".format(tag),
                        self._filename,
                        self._line
                    )

                type = self._tag_map[tag]
                token = Token(type, self._line, wscontrol)
                self._tokens.append(token)
                self._mode = self.MODE_TEXT
                pos += 2
                break

            # Unknown character in input
            raise SyntaxError(
                "Unexpected character {0}".format(ch),
                self._filename,
                self._line
            )

        # end while loop
        return pos

    def _parse_number(self, start):
        """ Parse a number. """
        result = []
        found_dot = False

        if self._text[start] == "-":
            start += 1
            result.append("-")
        elif self._text[start] == "+":
            start += 1

        for pos in range(start, len(self._text)):
            ch = self._text[pos]

            if ch in self._digit:
                result.append(ch)
                continue

            if ch == ".":
                if found_dot:
                    break

                result.append(ch)
                found_dot = True
                continue

            break

        result = "".join(result)
        if found_dot:
            token = Token(Token.TYPE_FLOAT, self._line, float(result))
        else:
            token = Token(Token.TYPE_INTEGER, self._line, int(result))

        self._tokens.append(token)
        return pos

    def _parse_string(self, start):
        """ Parse a string. """

        escaped = False
        result = []
        end = False
        for pos in range(start + 1, len(self._text)): # Skip opening quote
            ch = self._text[pos]

            if escaped:
                escaped = False
                if ch == "n":
                    result.append("\n")
                elif ch == "t":
                    result.append("\t")
                elif ch == "\\":
                    result.append("\\")
                elif ch == "\"":
                    result.append("\"")
                continue

            if ch == "\"":
                end = True
                break

            if ch == "\\":
                escaped = True
                continue

            result.append(ch)
            if ch == "\n":
                self._line += 1

        if not end:
            raise SyntaxError("Unclosed string", self._line)

        token = Token(Token.TYPE_STRING, self._line, "".join(result))
        self._tokens.append(token)
        return pos + 1

    def _parse_word(self, start):
        """ Parse a word. """
        result = []
        for pos in range(start, len(self._text)):
            ch = self._text[pos]

            if ch in self._alpha or ch in self._digit or ch in ("_", ".", "@", "#"):
                result.append(ch)
                continue
            else:
                break

        token = Token(Token.TYPE_WORD, self._line, "".join(result))
        self._tokens.append(token)

        return pos


class TemplateParser(object):
    """ A base tokenizer. """

    AUTOSTRIP_NONE = 0
    AUTOSTRIP_STRIP = 1
    AUTOSTRIP_TRIM = 2

    def __init__(self, template, text):
        """ Initialize the parser. """

        self._template = template
        self._text = text
        self._tokens = None
        self._token = None
        
        # Stack and line number
        self._ops_stack = []
        self._nodes = NodeList()
        self._stack = [self._nodes]

        # Buffer for plain text segments
        self._buffer = []
        self._pre_ws_control = Token.WS_NONE
        self._autostrip = self.AUTOSTRIP_NONE
        self._autostrip_stack = []

    def _get_token(self, pos, errmsg="Expected token"):
        """ Get a token at a position. """
        if pos < 0 or pos >= len(self._tokens):
            raise SyntaxError(
                errmsg,
                self._template._filename,
                self._token._line if self._token else 0
            )

        self._token = self._tokens[pos]
        return self._token

    def _expect_token(self, token, type, errmsg="Unexpected token"):
        if token._type != type:
            raise SyntaxError(
                errmsg,
                self._template._filename,
                token._line if token else 0
            )

    def _get_expected_token(self, pos, type, errmsg="Unexpected token"):
        """ Expect a specific type of token. """
        token = self._get_token(pos)
        self._expect_token(token, type, errmsg)
        return token

    def parse(self):
        """ Parse the template and return the node list. """
        
        self._parse_body()
        self._flush_buffer()

        if self._ops_stack:
            raise SyntaxError(
                "Unmatched action tag", 
                self._template._filename,
                self._ops_stack[-1][1]
            )

        return self._nodes

    def _parse_body(self):
        """ Parse the entire body. """

        tokenizer = Tokenizer(self._text, self._template._filename)
        self._tokens = tokenizer.parse()

        pos = 0
        while pos < len(self._tokens):

            token = self._token = self._tokens[pos]

            if token._type == Token.TYPE_TEXT:
                self._buffer.append(token._value)
                pos += 1
                continue

            if token._type in (Token.TYPE_START_COMMENT,
                              Token.TYPE_START_ACTION,
                              Token.TYPE_START_EMITTER):
                # Handle flushing the buffer
                self._flush_buffer(token._value)

                # Parse the tag
                if token._type == Token.TYPE_START_COMMENT:
                    pos = self._parse_tag_comment(pos + 1)
                elif token._type == Token.TYPE_START_ACTION:
                    pos =  self._parse_tag_action(pos + 1)
                elif token._type == Token.TYPE_START_EMITTER:
                    pos =  self._parse_tag_emitter(pos + 1)

                continue

            raise SyntaxError(
                "Unrecognized token",
                self._template._filename,
                self._token._line
            )

    def _parse_tag_ending(self, start, type):
        """ Parse an expected tag ending. """

        token = self._get_token(start, "Unclosed tag")
        if not token._type == type:
            raise SyntaxError(
                "Unexpected close tag",
                self._template._filename,
                token._line
            )

        self._pre_ws_control = token._value

        return start + 1

    def _parse_tag_comment(self, start):
        """ Parse a comment tag: """

        return self._parse_tag_ending(
            start,
            Token.TYPE_END_COMMENT
        )

    def _parse_tag_action(self, start):
        """ Parse some action tag. """
        
        # Determine the action
        token = self._get_token(start, "Expected action")
        action = token._value
        
        pos = start + 1
        if action == "if":
            pos = self._parse_action_if(pos)
        elif action == "elif":
            pos = self._parse_action_elif(pos)
        elif action == "else":
            pos =  self._parse_action_else(pos)
        elif action == "for":
            pos = self._parse_action_for(pos)
        elif action == "switch":
            pos = self._parse_action_switch(pos)
        elif action in SwitchNode.types:
            pos = self._parse_action_switch_item(pos, action)
        elif action == "set":
            pos = self._parse_action_set(pos, Scope.SCOPE_LOCAL)
        elif action == "global":
            pos = self._parse_action_set(pos, Scope.SCOPE_GLOBAL)
        elif action == "template":
            pos = self._parse_action_set(pos, Scope.SCOPE_TEMPLATE)
        elif action == "private":
            pos = self._parse_action_set(pos, Scope.SCOPE_PRIVATE)
        elif action == "unset":
            pos = self._parse_action_unset(pos)
        elif action == "scope":
            pos = self._parse_action_scope(pos)
        elif action == "code":
            pos = self._parse_action_code(pos)
        elif action == "include":
            pos = self._parse_action_include(pos)
        elif action == "return":
            pos = self._parse_action_return(pos)
        elif action == "expand":
            pos = self._parse_action_expand(pos)
        elif action == "section":
            pos = self._parse_action_section(pos)
        elif action == "use":
            pos = self._parse_action_use(pos)
        elif action == "def":
            pos = self._parse_action_def(pos)
        elif action == "call":
            pos = self._parse_action_call(pos)
        elif action == "var":
            pos = self._parse_action_var(pos)
        elif action == "error":
            pos = self._parse_action_error(pos)
        elif action == "import":
            pos = self._parse_action_import(pos)
        elif action == "do":
            pos = self._parse_action_do(pos)
        elif action.startswith("end"):
            pos = self._parse_action_end(pos, action)
        elif action == "strip":
            pos = self._parse_action_strip(pos)
        elif action == "autostrip":
            self._autostrip = self.AUTOSTRIP_STRIP
        elif action == "autotrim":
            self._autostrip = self.AUTOSTRIP_TRIM
        elif action == "no_autostrip":
            self._autostrip = self.AUTOSTRIP_NONE
        else:
            raise SyntaxError(
                "Unknown action tag: {0}".format(action),
                self._template._filename,
                token._line
            )

        return self._parse_tag_ending(pos, Token.TYPE_END_ACTION)

    def _parse_action_if(self, start):
        """ Parse an if action. """
        line = self._token._line
        (expr, pos) = self._parse_expr(start)
        
        node = IfNode(self._template, line, expr)
        
        self._ops_stack.append(("if", line))
        self._stack[-1].append(node)
        self._stack.append(node._nodes)
        return pos

    def _parse_action_elif(self, start):
        """ Parse an elif action. """
        line = self._token._line
        (expr, pos) = self._parse_expr(start)

        if not self._ops_stack:
            raise SyntaxError(
                "Mismatched elif",
                self._template._filename,
                line
            )

        what = self._ops_stack[-1]
        if what[0] != "if":
            raise SyntaxError(
                "Mismatched elif",
                self._template._filename,
                line
            )

        self._stack.pop()
        node = self._stack[-1][-1]
        node.add_elif(expr)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_else(self, start):
        """ Parse an else. """
        line = self._token._line
        if not self._ops_stack:
            raise SyntaxError(
                "Mismatched else",
                self._template._filename,
                line
            )

        what = self._ops_stack[-1]
        if not what[0] in ("if", "for"):
            raise SyntaxError(
                "Mismatched else",
                self._template._filename,
                line
            )

        # Both if and for do this the same way
        self._stack.pop()
        node = self._stack[-1][-1]
        node.add_else()
        self._stack.append(node._nodes)

        return start

    def _parse_action_for(self, start):
        """ Parse a for statement. """
        line = self._token._line
        (var, pos) = self._parse_topvar(start)

        token = self._get_token(pos, "Expected 'in'")
        if token._type == Token.TYPE_COMMA:
            (cvar, pos) = self._parse_topvar(pos + 1)
            token = self._get_token(pos, "Expected 'in'")
        else:
            cvar = None

        if token._type != Token.TYPE_WORD or token._value != "in":
            raise SyntaxError(
                "Expected 'in'",
                self._template._filename,
                token._line
            )

        (expr, pos) = self._parse_expr(pos + 1)

        node = ForNode(self._template, line, var, cvar, expr)
        self._ops_stack.append(("for", line))
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_switch(self, start):
        """ Parse a switch statement. """
        line = self._token._line
        (expr, pos) = self._parse_expr(start)

        node = SwitchNode(self._template, line, expr)
        self._ops_stack.append(("switch", line))
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_switch_item(self, start, item):
        """ Parse the switch item. """
        line = self._token._line

        if not self._ops_stack:
            raise SyntaxError(
                "{0} can only occur in switch".format(item),
                self._template._filename,
                line
            )

        what = self._ops_stack[-1]
        if what[0] != "switch":
            raise SyntaxError(
                "{0} can only occur in switch".format(item),
                self._template._filename,
                line
            )

        offset = SwitchNode.types.index(item)
        argc = SwitchNode.argc[offset]

        (exprs, pos) = self._parse_multi_expr(start, Token.TYPE_END_ACTION)

        if len(exprs) != argc:
            raise SyntaxError(
                "Switch clause {0} takes {1} argument".format(item, argc),
                self._template._filename,
                line
            )

        self._stack.pop()
        node = self._stack[-1][-1]
        node.add_case(SwitchNode.cbs[offset], exprs)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_set(self, start, where):
        """ Parse a set statement. """
        line = self._token._line

        (assigns, pos) = self._parse_multi_assign(start, Token.TYPE_END_ACTION)

        node = AssignNode(self._template, line, assigns, where)
        self._stack[-1].append(node)

        return pos

    def _parse_action_unset(self, start):
        """ Parse an unset statement. """
        line = self._token._line

        (varlist, pos) = self._parse_multi_topvar(start, Token.TYPE_END_ACTION)

        node = UnsetNode(self._template, line, varlist);
        self._stack[-1].append(node)

        return pos

    def _parse_action_scope(self, start):
        """ Parse a scope statement. """
        line = self._token._line

        (assigns, pos) = self._parse_multi_assign(start, Token.TYPE_END_ACTION)

        node = ScopeNode(self._template, line, assigns)
        self._ops_stack.append(("scope", line))
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_code(self, start):
        """ Parse a code node. """
        line = self._token._line
        pos = start

        # disable autostrip for this block
        self._autostrip_stack.append(self._autostrip)
        self._autostrip = self.AUTOSTRIP_NONE

        retvar = None
        token = self._get_token(pos)
        if token._type == Token.TYPE_WORD and token._value == "return":
            (retvar, pos) = self._parse_topvar(pos + 1)

        assigns = []
        token = self._get_token(pos)
        if token._type == Token.TYPE_WORD and token._value == "with":
            (assigns, pos) = self._parse_multi_assign(pos + 1, Token.TYPE_END_ACTION)

        self._ops_stack.append(("code", line))
        node = CodeNode(self._template, line, assigns, retvar)
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_include(self, start):
        """ Parse an include node. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)

        retvar = None
        token = self._get_token(pos)
        if token._type == Token.TYPE_WORD and token._value == "return":
            (retvar, pos) = self._parse_topvar(pos + 1)

        assigns = []
        token = self._get_token(pos)
        if token._type == Token.TYPE_WORD and token._value == "with":
            (assigns, pos) = self._parse_multi_assign(pos + 1, Token.TYPE_END_ACTION)

        node = IncludeNode(self._template, line, expr, assigns, retvar)
        self._stack[-1].append(node)

        return pos

    def _parse_action_return(self, start):
        """ Parse a return variable node. """
        line = self._token._line

        (assigns, pos) = self._parse_multi_assign(start, Token.TYPE_END_ACTION)

        node = ReturnNode(self._template, line, assigns)
        self._stack[-1].append(node)

        return pos

    def _parse_action_expand(self, start):
        """ Parse an expand node. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)

        node = ExpandNode(self._template, line, expr)
        self._stack[-1].append(node)

        return pos

    def _parse_action_section(self, start):
        """ Parse a section node. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)

        self._ops_stack.append(("section", line))
        node = SectionNode(self._template, line, expr)
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_use(self, start):
        """ Parse a use section node. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)

        node = UseSectionNode(self._template, line, expr)
        self._stack[-1].append(node)

        return pos

    def _parse_action_def(self, start):
        """ Parse a local or global def. """
        line = self._token._line

        token = self._get_token(start, "Expected string")
        if token._type != Token.TYPE_STRING:
            raise SyntaxError(
                "Expected string",
                self._template._filename,
                line
            )

        self._ops_stack.append(("def", line))

        nodes = self._template._defines.setdefault(token._value, NodeList())
        self._stack.append(nodes)

        return start + 1

    def _parse_action_call(self, start):
        """ Parse a call to a local or global def. """
        line = self._token._line

        token = self._get_token(start, "Expected string")
        if token._type != Token.TYPE_STRING:
            raise SyntaxError(
                "Expected string",
                self._template._filename,
                line
            )

        nodes = self._template._defines.get(token._value, None)
        if nodes is None:
            raise UnknownDefineError(
                name,
                self._template._filename,
                line
            )

        self._stack[-1].extend(nodes)

        return start + 1

    def _parse_action_var(self, start):
        """ Parse a block to store rendered output in a variable. """
        line = self._token._line

        (var, pos) = self._parse_topvar(start)

        node = VarNode(self._template, line, var)
        self._ops_stack.append(("var", line))
        self._stack[-1].append(node)
        self._stack.append(node._nodes)

        return pos

    def _parse_action_error(self, start):
        """ Raise an error from the template. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)
        node = ErrorNode(self._template, line, expr)
        self._stack[-1].append(node)

        return pos

    def _parse_action_import(self, start):
        """ Parse an import action. """

        (assigns, pos) = self._parse_multi_assign(start, Token.TYPE_END_ACTION)

        node = ImportNode(self._template, self._token._line, assigns)
        self._stack[-1].append(node)

        return pos

    def _parse_action_do(self, start):
        """ Parse a do tag. """

        (nodes, pos) = self._parse_multi_expr(start, Token.TYPE_END_ACTION)
        node = DoNode(self._template, self._token._line, nodes)
        self._stack[-1].append(node)

        return pos

    def _parse_action_end(self, start, action):
        """ Parse an end tag """
        line = self._token._line

        if not self._ops_stack:
            raise SyntaxError(
                "To many ends: {0}".format(action),
                self._template._filename,
                line
            )

        what = self._ops_stack[-1]
        if what[0] != action[3:]:
            raise SyntaxError(
                "Mismatched end tag: {0}".format(action),
                self._template._filename,
                line
            )

        self._ops_stack.pop()

        # Handle certain tags

        # Pop node stack for any op that created a new node stack
        if not what[0] == "strip":
            self._stack.pop()

        # Restore autostrip value for any op that pushed the value
        if what[0] in ("strip", "code"):
            self._autostrip = self._autostrip_stack.pop()

        return start

    def _parse_action_strip(self, start):
        """ Push autostrip and change the state. """
        line = self._token._line

        self._autostrip_stack.append(self._autostrip)
        self._ops_stack.append(("strip", line))

        token = self._get_token(start, "Expected on, off, or trim")
        if token._type == Token.TYPE_END_ACTION:
            # No change
            return start

        if token._type != Token.TYPE_WORD or not token._value in ("on", "off", "trim"):
            raise SyntaxError(
                "Expected on, off, or trim",
                self._template._filename,
                token._line
            )

        if token._value == "on":
            self._autostrip = self.AUTOSTRIP_STRIP
        elif token._value == "trim":
            self._autostrip = self.AUTOSTRIP_TRIM
        else:
            self._autostrip = self.AUTOSTRIP_NONE

        return start + 1

    def _parse_tag_emitter(self, start):
        """ Parse an emitter tag. """
        line = self._token._line

        (expr, pos) = self._parse_expr(start)
        pos = self._parse_tag_ending(pos, Token.TYPE_END_EMITTER)

        if isinstance(expr, ValueExpr):
            node = TextNode(self._template, line, str(expr.eval()))
        else:
            node = EmitNode(self._template, line, expr)
        self._stack[-1].append(node)
        return pos
        
    def _parse_expr(self, start):
        """ Parse an expression and return (node, pos) """

        token = self._get_token(start)
        if token._type in (Token.TYPE_STRING, Token.TYPE_FLOAT, Token.TYPE_INTEGER):
            node = ValueExpr(self._template, token._line, token._value)
            return (node, start + 1)

        if token._type == Token.TYPE_START_LIST:
            return self._parse_expr_list(start + 1)

        (var, pos) = self._parse_var(start)
        next = self._get_token(pos)
        if next._type == Token.TYPE_START_FUNC:
            (nodes, pos) = self._parse_multi_expr(pos + 1, Token.TYPE_END_FUNC)
            pos += 1 # skip past ")"
            node = FuncExpr(self._template, next._line, var, nodes)
        elif next._type == Token.TYPE_START_LIST:
            (nodes, pos) = self._parse_multi_expr(pos + 1, Token.TYPE_END_LIST)
            pos += 1 # skip past "]"
            node = IndexExpr(self._template, next._line, var, nodes)
        else:
            node = VarExpr(self._template, token._line, var)
          
        return (node, pos)

    def _parse_expr_list(self, start):
        """ Pare an expression that's a list. """
        (nodes, pos) = self._parse_multi_expr(start, Token.TYPE_END_LIST)
        pos += 1 # skip past "]"

        if nodes and all(isinstance(node, ValueExpr) for node in nodes):
            node = ValueExpr(self._template, nodes[0]._line, [node.eval() for node in nodes])
        else:
            node = ListExpr(self._template, self._token._line, nodes)
        return (node, pos)

    def _parse_multi_expr(self, start, ending):
        """ Parse a list of expressions
            Note: Return pos points at ending token.
        """
        items = []

        pos = start
        first = True
        while True:
            token = self._get_token(pos)
            if token._type == ending:
                return (items, pos)

            if not first:
                if token._type != Token.TYPE_COMMA:
                    raise SyntaxError(
                        "Expecting comma",
                        self._template._filename,
                        token._line
                    )
                pos += 1
            first = False

            (node, pos) = self._parse_expr(pos)
            items.append(node)

    def _parse_assign(self, start):
        """ Parse a var = expr assignment, return (var, expr, pos) """
        line = self._token._line

        (var, pos) = self._parse_topvar(start)

        token = self._get_expected_token(pos, Token.TYPE_EQUAL, "Expected '='")

        (expr, pos) = self._parse_expr(pos + 1)

        return (var, expr, pos)

    def _parse_multi_assign(self, start, ending):
        """ Parse multiple var = expr statemetns, return ( [(var, expr)], pos)
            Note: Return pos points at ending token.
        """
        assigns = []

        pos = start
        first = True
        while True:
            token = self._get_token(pos)
            if token._type == ending:
                return (assigns, pos)

            if not first:
                if not token._type == Token.TYPE_COMMA:
                    raise SyntaxError(
                        "Expecting comma",
                        self._template._filename,
                        token._line
                    )
                pos += 1
            first = False

            (var, expr, pos) = self._parse_assign(pos)
            assigns.append((var, expr))


    def _parse_var(self, start, allow_dots=True):
        """ Parse a variable and return (var, pos) """

        token = self._get_token(start, "Expected variable")
        if not token._type == Token.TYPE_WORD:
            raise SyntaxError(
                "Expected variable",
                self._template._filename,
                token._line
            )

        parts = token._value.split(".")
        if len(parts) > 1 and not allow_dots:
            raise SyntaxError(
                "Dotted variable not allowed",
                self._template._filename,
                token._line
            )

        for part in parts:
            if part[0:1] in ("@", "#"):
                part = part[1:]

            if not re.match("[a-zA-Z_][a-zA-Z0-9_]*", part):
                raise SyntaxError(
                    "Invalid variable name: {0}".format(token._value),
                    self._template._filename,
                    token._line
                )

        if allow_dots:
            result = parts
        else:
            result = parts[0]

        return (result, start + 1)

    def _parse_topvar(self, start):
        """ Parse a top-level variable (no dots). """
        return self._parse_var(start, False)

    def _parse_multi_var(self, start, ending, allow_dots=True):
        """ Parse multiple variables and return (varlist, pos)
            Note: Return pos points at ending token.
        """
        varlist = []

        pos = start
        first = True
        while True:
            token = self._get_token(pos)
            if token._type == ending:
                return (varlist, pos)

            if not first:
                if not token._type == Token.TYPE_COMMA:
                    raise SyntaxError(
                        "Expecting comma",
                        self._template._filename,
                        token._line
                    )
                pos += 1
            first = False

            (var, pos) = self._parse_var(pos, allow_dots)
            varlist.append(var)

    def _parse_multi_topvar(self, start, ending):
        """ Parse multiple topvars. """
        return self._parse_multi_var(start, ending, False)

    def _flush_buffer(self, post_ws_control=Token.WS_NONE):
        """ Flush the buffer to output. """
        text = ""
        if self._buffer:
            text = "".join(self._buffer)

            if self._autostrip == self.AUTOSTRIP_STRIP:
                text = text.strip()
            elif self._autostrip == self.AUTOSTRIP_TRIM:
                tmp = []
                need_nl = False
                for line in text.splitlines():
                    line = line.strip()
                    if line:
                        if need_nl:
                            tmp.append("\n")
                        tmp.append(line)
                        need_nl = True
                text = "".join(tmp)
            else:
                if self._pre_ws_control in (Token.WS_TRIMTONL, Token.WS_TRIMTONL_PRESERVENL):
                    # If the previous tag had a white-space control {{ ... -}}
                    # trim the start of this buffer up to/including a new line
                    # If the previous tag has a white-space control {{^ .. }}
                    # trim the start of the buffer up to but excluding a new line
                    first_nl = text.find("\n")
                    if first_nl == -1:
                        text = text.lstrip()
                    else:
                        nl = 1 if self._pre_ws_control == Token.WS_TRIMTONL else 0
                        text = text[:first_nl + nl].lstrip() + text[first_nl + nl:]

                if post_ws_control in (Token.WS_TRIMTONL, Token.WS_TRIMTONL_PRESERVENL):
                    # If the current tag has a white-space control {{- ... }}
                    # trim the end of the buffer up to/including a new line
                    # If the current tag has a white-space control {{^ .. }}
                    # trim the end of the buffer up to but excluding a new line
                    last_nl = text.rfind("\n")
                    if last_nl == -1:
                        text = text.rstrip()
                    else:
                        nl = 0 if post_ws_control == Token.WS_TRIMTONL else 1
                        text = text[:last_nl + nl] + text[last_nl + nl:].rstrip()
            
        if self._pre_ws_control == Token.WS_ADDNL:
            text = "\n" + text
        elif self._pre_ws_control == Token.WS_ADDSP:
            text = " " + text

        if post_ws_control == Token.WS_ADDNL:
            text = text + "\n"
        elif post_ws_control == Token.WS_ADDSP:
            text = text + " "

        if text:
            node = TextNode(self._template, self._token._line, text)
            self._stack[-1].append(node)

        self._buffer = []

