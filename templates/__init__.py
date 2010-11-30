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
    def shortest(g):
            return g.shortestChainLength()
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
            extend_(['    ', u'    <li>\n'])
            if m.user:
                extend_(['        ', u'    <img src="', escape_(m.user.picture, True), u'" alt="', escape_(m.user.username, True), u'" title="', escape_(m.user.username, True), u'" />\n'])
            else:
                extend_(['        ', u'    <div class="no-user"></div>\n'])
            extend_(['    ', u'    ', escape_(word(m, m.word), False), u' ', escape_(ts(m.played), False), u' ', escape_(form(m), False), u'\n'])
        if m.children:
            for c in loop.setup(m.children):
                extend_(['        ', u'    ', escape_(move(c, False), False), u'\n'])
            extend_(['    ', u'    </li>\n'])
        if m.bottom:
            extend_(['    ', u'    <li bottom>\n'])
            if m.user:
                extend_(['        ', u'    <img src="', escape_(m.user.picture, True), u'" alt="', escape_(m.user.username, True), u'" title="', escape_(m.user.username, True), u'" />\n'])
            else:
                extend_(['        ', u'    <div class="no-user"></div>\n'])
            extend_(['    ', u'    ', escape_(word(m, m.word), False), u' ', escape_(form(m), False), u'</li>\n'])
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
    self['title'] = join_(escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' ', escape_(finished(), True))
    self['css'] = join_(u'/static/css/game.css /static/css/jquery.gritter.css')
    self['js'] = join_(u'/static/js/jquery.periodicalupdater.js /static/js/jquery.shake.js /static/js/game.js /static/js/wire.js')
    extend_([u'<script type="text/javascript">\n'])
    extend_([u'var lastmove = ', escape_(game.lastmove, True), u';\n'])
    extend_([u'var done = ', escape_((game.done and "true" or "false"), True), u';\n'])
    for u in loop.setup(game.users):
        extend_([u"    users['", escape_((u), True), u"'] = {'username': '", escape_(game.users[u].username, False), u"', 'picture': '", escape_(game.users[u].picture, False), u"'};\n"])
    if game.done:
        extend_([u'    var winningchain = ', escape_((dump_json(game.done and game.winningchain or [])), True), u';\n'])
        extend_([u'    var scores = ', escape_((game.done and dump_json(game.score) or {}), False), u';\n'])
    for m in loop.setup(game.moves.values()):
        for c in loop.setup(m.children):
            extend_(['    ', u'    addLink(', escape_(m.id, True), u', ', escape_(c.id, True), u", '", escape_(((m.id in game.winningchain and c.id in game.winningchain) and 'red' or 'blue'), True), u"');\n"])
    if game.done:
        extend_([u'    addLink(', escape_(game.lastmove, True), u', ', escape_((filter(lambda m: m.id != game.lastmove and m.word == game.moves[game.lastmove].word, game.moves.values())[0].id), True), u", 'red');\n"])
    extend_([u'</script>\n'])
    extend_([u'<h1 id="game">', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' ', escape_(finished(), True), u'</h1>\n'])
    if game.done:
        extend_([u'    <ul id="scores">\n'])
        for s in loop.setup(game.scores()):
            extend_(['            ', u'    <li><img src="', escape_(game.scores()[s]['picture'], True), u'" alt="" title="" border="0" height="32" /> ', escape_(game.scores()[s]['username'], True), u' earned ', escape_(game.scores()[s]['score'], True), u' points</li>\n'])
        extend_([u'    </ul>\n'])
    extend_([escape_(move(game.moves[1], True), False), u'\n'])
    extend_([u'<br style="clear: left">\n'])
    extend_([escape_(move(game.moves[2], True), False), u'\n'])
    extend_([u'<p><a href="/">Back to game list</a>\n'])
    extend_([u'<div id="playinfo">', escape_(plays(), False), u'</div>\n'])

    return self

game = CompiledTemplate(game, 'templates/game.html')
join_ = game._join; escape_ = game._escape

# coding: utf-8
def layout (content):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html>\n'])
    extend_([u'        <head>\n'])
    extend_([u'                <title>Word Ladder: ', escape_(content.title, False), u'</title>\n'])
    extend_([u'                <link rel="icon" href="/static/images/favicon.png" />\n'])
    extend_([u'                <link rel="shortcut icon" href="/static/images/favicon.png" />\n'])
    extend_([u'                <meta name="viewport" content="width = device-width">\n'])
    extend_([u'                <link rel="stylesheet" href="/static/css/site.css" media="screen" />\n'])
    extend_([u'                <link rel="stylesheet" href="/static/css/humanmsg.css" media="screen" />\n'])
    if content.css:
        for css in loop.setup(content.css.split()):
            extend_(['            ', u'    <link rel="stylesheet" href="', escape_(css, False), u'" type="text/css" media="screen" />\n'])
        extend_(['        ', u'    <script type="text/javascript" src="http://www.google.com/jsapi"></script>\n'])
        extend_(['        ', u'    <script type="text/javascript">google.load(\'jquery\', \'1.3.2\');</script>\n'])
        extend_(['        ', u'    <script type="text/javascript" src="/static/js/humanmsg.js"></script>\n'])
    if content.js:
        for js in loop.setup(content.js.split()):
            extend_(['            ', u'    <script type="text/javascript" src="', escape_(js, False), u'"></script>\n'])
    extend_([u'        </head>\n'])
    extend_([u'        <body>\n'])
    extend_([u'                <div id="content">\n'])
    extend_([u'                        <div id="statusBar">\n'])
    extend_([u'                                <div id="logo">\n'])
    extend_([u'                                        <a href="/"><img src="/static/images/favicon.png" title="Word Ladder" alt="Word Ladder" width="16" height="16" border="0" /></a>\n'])
    extend_([u'                                        <a href="/">Word Ladder</a>\n'])
    extend_([u'                                </div>\n'])
    extend_([u'                                <div id="loggedIn">\n'])
    extend_([u'                                                <a href="/user/account" title="Your account"><img src="', escape_(currentUser().picture, True), u'" width="16" height="16" border="0" alt="', escape_(currentUser().username, True), u'" title="', escape_(currentUser().username, True), u'"></a>\n'])
    if currentUser().isAnonymous():
        extend_(['                                        ', u'    <a href="/user/account" title="Your account">Guest</a>\n'])
    else:
        extend_(['                                        ', u'    <a href="/user/account" title="Your account">', escape_(currentUser().username, True), u'</a>\n'])
        for s in loop.setup(currentUser().services):
            extend_(['                                            ', u'    <a href="', escape_(s.url, True), u'" title="', escape_(s.username, True), u' on ', escape_(s.name, True), u'"><img src="/static/images/', escape_((s.name), True), u'.png" title="', escape_(s.name, True), u'" width="16" height="16" border="0" /></a>\n'])
        extend_(['                                        ', u'    <a href="/user/logout" title="Log out" class="button" id="logout-button">Log out</a>\n'])
    extend_([u'                                </div>\n'])
    extend_([u'                                <div id="points">\n'])
    extend_([u'                                        <a href="/user/stats">\n'])
    extend_([u'                                                ', escape_(currentUser().score, True), u' total points\n'])
    if currentUser().isAnonymous() and currentUser().score:
        extend_(['                                                ', u'    &mdash; <a href="/user/account">Log in to claim these points</a>\n'])
    extend_([u'                                        </a>\n'])
    extend_([u'                                        <div class="popup">\n'])
    extend_([u'                                                games popup                                                     \n'])
    extend_([u'                                        </div>\n'])
    extend_([u'                                </div>\n'])
    extend_([u'                                <div id="actions">\n'])
    extend_([u'                                        <a href="/new">New Game</a>\n'])
    extend_([u'                                </div>\n'])
    extend_([u'                        </div>\n'])
    extend_([u'                        <div id="body">\n'])
    extend_([u'        ', escape_(content, False), u'\n'])
    extend_([u'                        </div>\n'])
    extend_([u'                </div>\n'])
    extend_([u'        </body>\n'])
    extend_([u'</html>\n'])

    return self

layout = CompiledTemplate(layout, 'templates/layout.html')
join_ = layout._join; escape_ = layout._escape

# coding: utf-8
def play(game, word, reason):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    extend_([u'<!DOCTYPE html>\n'])
    extend_([u'<html><head><title>Word Ladder: ', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' - Error</title>\n'])
    extend_([u'<link rel="icon" href="/static/images/favicon.png">\n'])
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
    self['title'] = join_(u'Welcome')
    self['css'] = join_()
    self['js'] = join_()
    __lineoffset__ -= 3
    def gamelist(gl, active, user=None):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'<ul>\n'])
        for g in loop.setup(gl):
            if g.done != active:
                extend_(['  ', u'<li><a href="/game/', escape_(g.key().name(), True), u'">', escape_(g.start.word, True), u' &rarr; ', escape_(g.end.word, True), u'</a>\n'])
                if user and user.key().name() in g.score:
                    extend_(['                          ', u'    (you earned ', escape_(g.score[user.key().name()]['score'], True), u' points)\n'])
                extend_(['  ', u'                        </li>\n'])
        extend_([u'</ul>\n'])
        return self
    extend_([u'<h1>Word Ladder</h1>\n'])
    extend_([u'<p>word &rarr; ward &rarr; wad &rarr; wade &rarr; waded &rarr; warded &rarr; wadder &rarr; ladder</p>\n'])
    extend_([u'<a href="/new"><span id="newgame">New Game</span></a>\n'])
    extend_([u'<h2>Unsolved Games:</h2>\n'])
    extend_([escape_(gamelist(games, True), False), u'\n'])
    extend_([u'<h2>Solved Games:</h2>\n'])
    extend_([escape_(gamelist(games, False, user), False), u'\n'])

    return self

index = CompiledTemplate(index, 'templates/index.html')
join_ = index._join; escape_ = index._escape

# coding: utf-8
def user(user, services):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    self['title'] = join_(u'Your Account')
    self['css'] = join_()
    self['js'] = join_()
    extend_([u'<h1>Your Account</h1>\n'])
    if user:
        if user.score and user.isAnonymous():
            extend_(['    ', u'    <h2>Log in to claim your points</h2>\n'])
            extend_(['    ', u"    <p>You've earned points, but you're still using a guest account. Log into one of the services below to claim your account and your points.</p>\n"])
            extend_(['    ', u'\n'])
        if len(services) > user.services.count():
            extend_(['    ', u'    <h2>Available services</h2>\n'])
            extend_(['    ', u'    <p>You can link your word ladder account to these services to be more social.</p>\n'])
            extend_(['    ', u'    <ul id="servicesavailable">\n'])
            for s in loop.setup(services):
                if s not in [us.name for us in user.services]:
                    extend_(['            ', u'    <li><a href="/user/login/', escape_(s, True), u'" title="Link a ', escape_(s, True), u' account">', escape_(s, True), u'</a></li>\n'])
            extend_(['    ', u'    </ul>\n'])
            extend_(['    ', u'\n'])
        if user.services.count():
            extend_(['    ', u'    <h2>Linked services</h2>\n'])
            extend_(['    ', u"    <p>You've linked your word ladder account to these services.</p>\n"])
            extend_(['    ', u'    <ul id="serviceslinked">\n'])
            for s in loop.setup(user.services):
                extend_(['        ', u'    <li>\n'])
                if s.picture:
                    extend_(['            ', u'    <img src="', escape_(s.picture, True), u'" border="0" height="50" alt="', escape_(str(user), True), u' on ', escape_(s.name, True), u'" />\n'])
                extend_(['        ', u'    ', escape_(s.name, True), u'\n'])
                extend_(['        ', u'    [<a href="/user/update/', escape_(s.name, True), u'" title="Update ', escape_(s.name, True), u' profile">update profile</a>]\n'])
                extend_(['        ', u'    [<a href="/user/remove/', escape_(s.name, True), u'" title="Unlink ', escape_(s.name, True), u'">unlink</a>]\n'])
                if s.picture and s.picture != user.picture:
                    extend_(['            ', u'    [<a href="/user/usephoto/', escape_(s.name, True), u'" title="Use ', escape_(s.name, True), u' photo">use photo</a>]\n'])
                extend_(['        ', u'    </li>\n'])
            extend_(['    ', u'    </ul>\n'])
            extend_(['    ', u'\n'])
        extend_([u'    <h2>Username</h2>\n'])
        if user.username:
            extend_(['    ', u'    <p>Your username is <span class="username">', escape_(user.username, True), u'</span>.</p>\n'])
        else:
            extend_(['    ', u'    <p>You have not chosen a username yet. You can choose one using the form below.</p>\n'])
        extend_([u'    <form action="/user/account" method="post">\n'])
        extend_([u'            <label for="username">Change username: <input type="text" name="username" id="username" size="23" maxlength="32" /></label>\n'])
        extend_([u'            <input type="hidden" name="return_to" value="/user/account" />\n'])
        extend_([u'            <button type="submit">Go</button>\n'])
        extend_([u'    </form>\n'])
    else:
        extend_([u'<p>You are not logged in.</p>\n'])

    return self

user = CompiledTemplate(user, 'templates/user.html')
join_ = user._join; escape_ = user._escape

