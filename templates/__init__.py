from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def game(game):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    
    def finished():
            if game.done:
                    return "(finished)"
            return ""
    def lasttenmoves(g):
            return [g.moves[i] for i in sorted(g.moves.keys(), reverse=True)[:10]]
    __lineoffset__ -= 3
    def form(m):
        self = TemplateResult(); extend_ = self.extend
        if not game.done:
            extend_(['    ', u'    <form method="POST" action=""><input type="hidden" name="moveid" value="', escape_(m.id, True), u'"><input type="text" name="word" autocomplete="off" autocorrect="off" autocapitalize="off"></input></form>\n'])
        else:
            extend_(['    ', u'    <div class="placeholder"></div>\n'])
        return self
    __lineoffset__ -= 3
    def word(m, w):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'            <a id="m', escape_((m.id), True), u'" class="move', escape_((m.id in game.winningchain and ' win' or ''), True), u'">', escape_(w, True), u'</a>\n'])
        return self
    __lineoffset__ -= 3
    def ts(t):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'    <span class="timestamp">', escape_(t, True), u'</span>\n'])
        return self
    __lineoffset__ -= 3
    def move(m, s):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'    <ul>\n'])
        if not m.bottom:
            extend_(['    ', u'    <li>', escape_(word(m, m.word), False), u' ', escape_(ts(m.played), False), u' ', escape_(form(m), False), u'\n'])
        if m.children:
            for c in loop.setup(m.children):
                extend_(['        ', u'    ', escape_(move(c, False), False), u'\n'])
        if m.bottom:
            extend_(['    ', u'    <li bottom>', escape_(word(m, m.word), False), u' ', escape_(form(m), False), u'\n'])
        extend_([u'    </ul>\n'])
        return self
    __lineoffset__ -= 3
    def plays():
        self = TemplateResult(); extend_ = self.extend
        for m in loop.setup(lasttenmoves(game)):
            if m.hasValidUser:
                extend_(['        ', u'    <span class="log">', escape_(m.user, True), u' played ', escape_(m.word, True), u'</span>\n'])
            else:
                extend_(['        ', u'    <span class="log">unknown user played ', escape_(m.word, True), u'</span>\n'])
        return self
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html><head><title>Word Ladder: ', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' ', escape_(finished(), True), u'</title>\n'])
    extend_([u'<link rel="stylesheet" type="text/css" href="/static/css/site.css">\n'])
    extend_([u'<link rel="stylesheet" type="text/css" href="/static/css/humanmsg.css">\n'])
    extend_([u'<link rel="stylesheet" type="text/css" href="/static/css/jquery.gritter.css">\n'])
    extend_([u'<link rel="icon" href="/static/favicon.png">\n'])
    extend_([u'<meta name="viewport" content="width = device-width, user-scalable=no">\n'])
    extend_([u'<script type="text/javascript" src="http://www.google.com/jsapi"></script>\n'])
    extend_([u'<script type="text/javascript">google.load(\'jquery\', \'1.3.2\');</script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/humanmsg.js"></script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/jquery.gritter.js"></script>\n'])
    extend_([u'<script type="text/javascript">\n'])
    extend_([u'var lastmove = ', escape_(game.lastmove, True), u';\n'])
    extend_([u'var done = ', escape_((game.done and "true" or "false"), True), u';\n'])
    extend_([u'var winningchain = ', escape_((game.done and game.winningchain or []), True), u';\n'])
    extend_([u'</script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/game.js"></script>\n'])
    extend_([u'<script type="text/javascript" src="/static/js/wire.js"></script>\n'])
    extend_([u'<script type="text/javascript">\n'])
    for m in loop.setup(game.moves.values()):
        for c in loop.setup(m.children):
            extend_(['    ', u'    addLink(', escape_(m.id, True), u', ', escape_(c.id, True), u", '", escape_(((m.id in game.winningchain and c.id in game.winningchain) and 'red' or 'blue'), True), u"');\n"])
    if game.done:
        extend_([u'    addLink(', escape_(game.lastmove, True), u', ', escape_((filter(lambda m: m.id != game.lastmove and m.word == game.moves[game.lastmove].word, game.moves.values())[0].id), True), u", 'red');\n"])
    extend_([u'</script>\n'])
    extend_([u'</head>\n'])
    extend_([u'<body>\n'])
    extend_([u'<h1>', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' ', escape_(finished(), True), u'</h1>\n'])
    extend_([escape_(move(game.moves[1], True), False), u'\n'])
    extend_([u'<br style="clear: left">\n'])
    extend_([escape_(move(game.moves[2], True), False), u'\n'])
    extend_([u'<p><a href="/">Back to game list</a>\n'])
    extend_([u'<div id="playinfo">', escape_(plays(), False), u'</div>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

game = CompiledTemplate(game, 'templates/game.html')
join_ = game._join; escape_ = game._escape

# coding: utf-8
def play(game, word, reason):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html><head><title>Word Ladder: ', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' - Error</title>\n'])
    extend_([u'<link rel="icon" href="/static/favicon.png">\n'])
    extend_([u'<meta http-equiv="refresh" content="2;URL=/game/', escape_((game.start), True), u'-', escape_((game.end), True), u'">\n'])
    extend_([u'<meta name="viewport" content="width = device-width">\n'])
    extend_([u'</head>\n'])
    extend_([u'<body>\n'])
    extend_([u'<h1>You cannot play the word ', escape_(word, True), u' there</h1>\n'])
    extend_([u'<p>', escape_(reason, True), u'\n'])
    extend_([u'<p><a href="/game/', escape_((game.start), True), u'-', escape_((game.end), True), u'">Back to the game</a>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

play = CompiledTemplate(play, 'templates/play.html')
join_ = play._join; escape_ = play._escape

# coding: utf-8
def index(games, user):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    __lineoffset__ -= 3
    def gamelist(gl, active):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'<ul>\n'])
        for g in loop.setup(gl):
            if g.done != active:
                extend_(['  ', u'<li><a href="/game/', escape_(g.key().name(), True), u'">', escape_(g.start.word, True), u' &rarr; ', escape_(g.end.word, True), u'</a>\n'])
        extend_([u'</ul>\n'])
        return self
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html><head><title>Word Ladder</title>\n'])
    extend_([u'<link rel="icon" href="/static/images/favicon.png">\n'])
    extend_([u'<meta name="viewport" content="width = device-width">\n'])
    extend_([u'</head>\n'])
    extend_([u'<body>\n'])
    if user:
        extend_([u'    <h1>Hi,\n'])
        if user.isAnonymous():
            extend_(['    ', u'    <a href="/user/account">', escape_(str(user), True), u'</a>!</h1>\n'])
            extend_(['    ', u'    <p>[<a href="/user/login/facebook">Facebook Login</a>] [<a href="/user/login/google">Google Buzz Login</a>]</p>\n'])
        else:
            if user.picture:
                extend_(['        ', u'    <img src="', escape_(user.picture, True), u'" border="0" height="50" alt="', escape_(str(user), True), u'" /> <a href="/user/account">', escape_(str(user), True), u'</a>!</h1>\n'])
            else:
                extend_(['        ', u'    <a href="/user/account">', escape_(str(user), True), u'</a>!</h1>\n'])
            extend_(['    ', u'    <p>[<a href="/user/logout">Log out</a>]</p>\n'])
            extend_(['    ', u'    <p>Your accounts:</p>\n'])
            extend_(['    ', u'    <ul>\n'])
            for s in loop.setup(user.services):
                extend_(['        ', u'    <li>\n'])
                if s.picture:
                    extend_(['            ', u'    <img src="', escape_(s.picture, True), u'" border="0" height="50" alt="', escape_(str(user), True), u' on ', escape_(s.name, True), u'" />\n'])
                extend_(['        ', u'    <a href="', escape_(s.url, True), u'">', escape_(s.name, True), u'</a></li>\n'])
            extend_(['    ', u'    </ul>\n'])
    else:
        extend_([u'    <p>[<a href="/user/login/facebook">Facebook Login</a>] [<a href="/user/login/google">Google Buzz Login</a>]</p>\n'])
    extend_([u'<h1>Active Games:</h1>\n'])
    extend_([escape_(gamelist(games, True), False), u'\n'])
    extend_([u'<h2>Finished Games:</h2>\n'])
    extend_([escape_(gamelist(games, False), False), u'\n'])
    extend_([u'<a href="new">New Game</a>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

index = CompiledTemplate(index, 'templates/index.html')
join_ = index._join; escape_ = index._escape

# coding: utf-8
def user(user):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html><head><title>Word Ladder: Your Account</title>\n'])
    extend_([u'<body>\n'])
    extend_([u'<h1>Your Account</h1>\n'])
    if user:
        if user.username:
            extend_([u'<p>Your username is <span class="username">', escape_(user.username, True), u'</span>. You can change it using the form below.</p>\n'])
        else:
            extend_([u'<p>You have not chosen a username yet. You can choose one using the form below.</p>\n'])
        extend_([u'<form action="/user/account" method="post">\n'])
        extend_([u'  <label for="username">Username: <input type="text" name="username" id="username" size="23" maxlength="32" /></label>\n'])
        extend_([u'  <input type="hidden" name="return_to" value="/user/account" />\n'])
        extend_([u'  <button type="submit">Set Username</button>\n'])
        extend_([u'</form>\n'])
    else:
        extend_([u'<p>You are not logged in. Please log in using OpenID.</p>\n'])
        extend_([u'<form method="post" action="/user/login">\n'])
        extend_([u'  <label for="openid">Open ID: <input type="text" name="openid" id="openid" value="" /></label>\n'])
        extend_([u'  <input type="hidden" name="return_to" value="/user/account" />\n'])
        extend_([u'  <button type="submit">Login</button>\n'])
        extend_([u'</form>\n'])
    extend_([u'</body>\n'])
    extend_([u'</html>\n'])

    return self

user = CompiledTemplate(user, 'templates/user.html')
join_ = user._join; escape_ = user._escape

