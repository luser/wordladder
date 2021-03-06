from web.template import CompiledTemplate, ForLoop, TemplateResult


# coding: utf-8
def game(game, user):
    __lineoffset__ = -4
    loop = ForLoop()
    self = TemplateResult(); extend_ = self.extend
    
    def finished():
            if game.done:
                    return "(finished)"
            return ""
    def shortest(g):
            return g.shortestChainLength()
    __lineoffset__ -= 3
    def form(l, m):
        self = TemplateResult(); extend_ = self.extend
        if not game.done:
            extend_(['    ', u'    <form method="POST" autocomplete="off"><input type="hidden" name="moveid" value="', escape_(m.id, True), u'"><input type="hidden" name="ladderid" value="', escape_(l.id, True), u'"><input type="text" name="word" autocomplete="off" autocorrect="off" autocapitalize="off"></form>\n'])
        else:
            extend_(['    ', u'    <div class="placeholder"></div>\n'])
        return self
    __lineoffset__ -= 3
    def word(l, m, w):
        self = TemplateResult(); extend_ = self.extend
        extend_([u'    <a id="l', escape_((l.id), True), u'm', escape_((m.id), True), u'" class="move move', escape_((m.id), True), u'">\n'])
        if not game.done:
            if m.bottom:
                extend_(['        ', u'    <img src="/static/images/add.png" alt="Add a word" title="Add a word" class="addword bottom" />\n'])
            else:
                extend_(['        ', u'    <img src="/static/images/add.png" alt="Add a word" title="Add a word" class="addword" />\n'])
        if m.user:
            extend_(['    ', u'    <img src="', escape_(m.user.picture, True), u'" alt="', escape_(m.user.username, True), u'" title="', escape_(m.user.username, True), u'" />\n'])
        else:
            extend_(['    ', u'    <div class="no-user"></div>\n'])
        extend_([u'    ', escape_(w, True), u'\n'])
        extend_([u'    </a>\n'])
        return self
    __lineoffset__ -= 3
    def drawladder(l, bottom):
        self = TemplateResult(); extend_ = self.extend
        if bottom == l.bottom:
            extend_(['    ', u'    <div class="ladder-container">\n'])
            extend_(['    ', u'    <div class="ladder-width"></div>\n'])
            ladder = l.ladder
            if not bottom:
                extend_(['        ', u'    ', escape_(ladder.reverse(), True), u'\n'])
            extend_(['    ', u'    <ul id="l', escape_((l.id), True), u'">\n'])
            for r in loop.setup(ladder):
                extend_(['        ', u'    <li>\n'])
                if bottom:
                    extend_(['            ', u'    ', escape_(form(l, r), False), u'\n'])
                extend_(['        ', u'    ', escape_(word(l, r, r.word), False), u'\n'])
                if not bottom:
                    extend_(['            ', u'    ', escape_(form(l, r), False), u'\n'])
                extend_(['        ', u'    </li>\n'])
            extend_(['    ', u'    </ul>\n'])
            extend_(['    ', u'    </div>\n'])
        return self
    self['title'] = join_(escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' (', escape_(game.difficulty_rating, True), u') ', escape_(finished(), True))
    self['css'] = join_(u'/static/css/game.css')
    self['js'] = join_(u'/static/js/jquery.periodicalupdater.js /static/js/jquery.shake.js /static/js/game.js')
    extend_([u'<h1 id="game">', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' (', escape_(game.difficulty_rating, True), u') ', escape_(finished(), True), u'</h1>\n'])
    if game.done:
        extend_([u'    <ul id="scores">\n'])
        for s in loop.setup(game.scores()):
            extend_(['            ', u'    <li><img src="', escape_(game.scores()[s]['picture'], True), u'" alt="" title="" border="0" height="32" /> ', escape_(game.scores()[s]['username'], True), u' earned ', escape_(game.scores()[s]['score'], True), u' points</li>\n'])
        extend_([u'    </ul>\n'])
    extend_([u'<div id="top-ladder" class="ladder-set">\n'])
    for l in loop.setup(game.leaves):
        extend_([u'    ', escape_(drawladder(l, False), False), u'\n'])
    extend_([u'</div>\n'])
    extend_([u'<hr style="clear: both;"/>\n'])
    extend_([u'<div id="bottom-ladder" class="ladder-set">\n'])
    for l in loop.setup(game.leaves):
        extend_([u'    ', escape_(drawladder(l, True), False), u'\n'])
    extend_([u'</div>\n'])
    extend_([u'<p><a href="/">Back to game list</a>\n'])
    extend_([u'<script type="text/javascript">\n'])
    extend_([u'        var lastmove = ', escape_(game.lastmove, True), u';\n'])
    extend_([u'        var done = ', escape_((game.done and "true" or "false"), True), u';\n'])
    extend_([u"        var userid = '", escape_(user.key().name(), False), u"';\n"])
    extend_([u'        var users = {};\n'])
    for u in loop.setup(game.users):
        extend_([u"    users['", escape_((u), True), u"'] = {'username': '", escape_(game.users[u].username, False), u"', 'picture': '", escape_(game.users[u].picture, False), u"'};\n"])
    if game.done:
        extend_([u'    var winningchain = ', escape_((dump_json(game.done and game.winningchain or [])), True), u';\n'])
        extend_([u'    var scores = ', escape_((game.done and dump_json(game.score) or {}), False), u';\n'])
    extend_([u'</script>\n'])

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
    self['title'] = join_(u'Word Ladder; ', escape_(game.start, True), u' &rarr; ', escape_(game.end, True), u' - Error')
    self['css'] = join_()
    self['js'] = join_()
    extend_([u'<h1>You cannot play the word ', escape_(word, True), u' there</h1>\n'])
    extend_([u'<p>', escape_(reason, True), u'</p>\n'])
    extend_([u'<p><a href="/game/', escape_((game.start), True), u'-', escape_((game.end), True), u'">Back to the game</a></p>\n'])

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
        extend_([u'<dl>\n'])
        for g in loop.setup(gl):
            if g.done != active:
                extend_(['  ', u'<dt><a href="/game/', escape_(g.key().name(), True), u'">', escape_(g.start.word, True), u' &rarr; ', escape_(g.end.word, True), u'</a></dt>\n'])
                extend_(['  ', u'                        <dd>\n'])
                extend_(['  ', u'                        <ul>\n'])
                extend_(['  ', u'                        <li>Difficulty: <strong>', escape_(g.difficulty_rating, True), u'</strong></li>\n'])
                extend_(['  ', u'                        <li>Started: <strong>', escape_(g.start.played, True), u'</strong></li>\n'])
                if g.done:
                    extend_(['                          ', u'    <li>Completed: <strong>', escape_(g.moves[g.lastmove].played, True), u'</strong></li>\n'])
                    if user and user.key().name() in g.score:
                        extend_(['                              ', u'    <li>You earned: <strong>', escape_(g.score[user.key().name()]['score'], True), u'</strong> points</li>\n'])
                extend_(['  ', u'                        </ul>\n'])
                extend_(['  ', u'                        </dd>\n'])
        extend_([u'</dl>\n'])
        return self
    extend_([u'<h1>Word Ladder</h1>\n'])
    extend_([u'<p>word &rarr; ward &rarr; wared &rarr; warded &rarr; wadder &rarr; ladder</p>\n'])
    extend_([u'<a href="/new"><span id="newgame">New Game (Random)</span></a>\n'])
    extend_([u'<a href="/new/simple"><span id="newgame">New Game (Simple)</span></a>\n'])
    extend_([u'<a href="/new/easy"><span id="newgame">New Game (Easy)</span></a>\n'])
    extend_([u'<a href="/new/medium"><span id="newgame">New Game (Medium)</span></a>\n'])
    extend_([u'<a href="/new/hard"><span id="newgame">New Game (Hard)</span></a>\n'])
    extend_([u'<a href="/new/genius"><span id="newgame">New Game (Genius)</span></a>\n'])
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

