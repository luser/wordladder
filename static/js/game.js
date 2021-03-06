var DEFAULT_POLLTIME = 2000;
var update = -1;
var users = {};
var centered = {};

function handleSubmit (event) {
  var form = this;
  $.ajax({type: 'POST',
          url: document.location.href,
          data: {'lastmove': lastmove, 'word': form.word.value, 'moveid': form.moveid.value},
          dataType: 'json',
          beforeSend: function(req) { req.setRequestHeader('Accept', 'text/json'); },
          success: function(data) { handlePlayResponse(form, data); },
          error: function(req, err, ex) { handlePlayError(form, err); }
         });
  //TODO: throbber, color box, etc?
  event.preventDefault();
}

function handlePlayResponse (form, data) {
  if ('error' in data) {
    $(form.word).addClass('error').shake(3, 4, 240);
    humanMsg.displayMsg(data.error);
  } else {
    // success
    form.word.value = '';
    $(form.word).removeClass('error');
    $(form).slideUp('fast');
  }
  handleGameJSON(data, $(form).parent().parent());
  if (!('error' in data) && !('done' in data)) {
    // focus the textbox under the word the user just played
    $('a.move' + lastmove).click();
  }
}

function handlePlayError (form, err) {
  // TODO: network error icon or something
}

function handleGameJSON (data, ladder) {
  if ('done' in data && !done) {
    done = data.done;
		update.stop();
    // TODO: fancy this up
    document.title += " (finished)";
    $('h1').append(" (finished)");
		$('#game').after('<ul id="scores"></ul>');
		for (user in data.scores) {
			$('#scores').append('<li><img src="'+data.scores[user]['picture']+'" alt="" title="" border="0" height="32" /> '+data.scores[user]['username']+' earned '+data.scores[user]['score']+' points.</li>');
		}
  }
  $.each(data.moves, function(i, m) {
		if (m.id > lastmove) {
      if ('userid' in m && !(m.userid in users)) {
      	if ('username' in m) username = m.username;
	      else username = "Guest";
			  if ('picture' in m) picture = m.picture;
				else picture = 'http://www.google.com/s2/static/images/NoPicture.gif';

				users[m.userid] = {'username': username, 'picture': picture}
			} else {
				username = users[m.userid]['username'];
				picture = users[m.userid]['picture'];
			}
			
			// If this move creates a branch, duplicate the ladder up to the previous move.
			var newBranch = false;
			if (!ladder || m.userid != userid) ladder = $('a.move' + m.parent + ':last').parent().parent();
			$(ladder).children('li').each(function (i, e) {
				moveid = parseInt($(e).children('a').attr('id').replace($(ladder).attr('id') + 'm', ''), 10);
				if (moveid > m.parent) newBranch = true;
			});

			if (newBranch) {
				newLadder = $(document.createElement('ul'));
				newLadder.attr('id', 'l' + m.id);
				$(ladder).children('li').each(function (i, e) {
					moveid = parseInt($(e).children('a').attr('id').replace($(ladder).attr('id') + 'm', ''), 10);
					if (moveid <= m.parent) {
						newMove = $(e).clone().removeClass('active');
						newMove.children('a').attr('id', newLadder.attr('id') + 'm' + moveid);
						newMove.children('a').click(moveClick).nextAll('form').submit(handleSubmit).children('input[name="word"]').keypress(keybdNav);
						newMove.appendTo(newLadder);
					}
				});
			} else newLadder = $(ladder);

			// Add the new move.
	    var html =  '<li' + (m.bottom?' bottom':'') + '>';
					if (!m.bottom) {
						html += '<a id="' + newLadder.attr('id') + 'm' + m.id + '" class="move move' + m.id + '">';
				    html += '<img src="/static/images/add.png" alt="Add a word" title="Add a word" class="addword" /> ';
				    html += '<img src="' + picture + '" alt="' + username + '" title="' + username + '" /> ';
						html += m.word + '</a>';
					}
					html += '<form method="POST" style="display: none;" autocomplete="off">';
					html += '<input type="hidden" name="moveid" value="' + m.id + '" />';
					html += '<input type="hidden" name="ladderid" value="' + newLadder.attr('id') + '" />';
					html += '<input type="text" id="' + newLadder.attr('id') + 'i' + m.id + '" name="word" autocomplete="off" autocorrect="off" autocapitalize="off" />';
					html += '</form>';
					if (m.bottom) {
						html += '<a id="' + newLadder.attr('id') + 'm' + m.id + '" class="move move' + m.id + '">';
				    html += '<img src="/static/images/add.png" alt="Add a word" title="Add a word" class="addword bottom" /> ';
				    html += '<img src="' + picture + '" alt="' + username + '" title="' + username + '" /> ';
						html += m.word + '</a>';
					}
					html += '</li>';
			
			if (m.bottom) newLadder.prepend(html);
			else newLadder.append(html);			

			// Put the new ladder next to the old one.
			if (newBranch) {
				var newContainer = $(document.createElement('div')).addClass('ladder-container').hide().css('opacity', 0);
				var newProp = $(document.createElement('div')).addClass('ladder-width');
				$(newContainer).append(newProp).append(newLadder);
				$(ladder).parent().after(newContainer);
				$(newContainer).animate({width: 'show'}, {duration: 300, queue: true});
				$(newContainer).animate({opacity: 1}, {duration: 300, queue: true, complete: function () { centerLadder($(newContainer).closest('.ladder-set'), $(newContainer)); }});
			}

			// Hide the old form.
			$('form').slideUp('fast');

			// Set up handlers for new move.
	    $('#' + newLadder.attr('id') + 'm' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).siblings('form').submit(handleSubmit).children('input[name="word"]').keydown(keybdNav);;
		}
	});
  if ('done' in data) {
		$('a.move').unbind('click').removeClass('active');

		// Hide interactive stuff.
		$('form').slideUp('fast').remove();
		$('img.addword').fadeOut('fast');

		highlightWinningLadders(data.lastmove, data.winningchain);

		// Center the winning ladders.
		centerLadder($('#top-ladder'), $('#top-ladder a.win:first').closest('.ladder-container'));
		centerLadder($('#bottom-ladder'), $('#bottom-ladder a.win:first').closest('.ladder-container'));
		$('a.win').removeClass('faded');
		$('a.move:not(.win)').addClass('faded');
	}
  if (data.lastmove > lastmove) lastmove = data.lastmove;
}

function highlightWinningLadders (last_move, winning_chain) {
	var lmove = $('a.move' + last_move);
	$(lmove).addClass('win').closest('li').siblings().children('a').addClass('win');
	var found = false;
	$(lmove).closest('.ladder-set').siblings('.ladder-set').children('.ladder-container').each(function(i, c) {
		$(c).find('a.move').each(function (i, m) {
			var moveid = String($(m).attr('id')).replace($(m).closest('ul').attr('id') + 'm', '');
			if ((moveid in oc(winning_chain)) && $.trim($(m).text()) == $.trim($(lmove).text()) && !found) {
				if ($(c).closest('.ladder-set').attr('id') == 'top-ladder') $(m).addClass('win').parent().prevAll('li').children('a').addClass('win');
				else $(m).addClass('win').parent().nextAll('li').children('a').addClass('win');
				found = true;
			}
		});
	});
}

function centerLadder (set, ladder) {
	$(centered[set.attr('id')]).removeClass('active');
	ladder.addClass('active');
	var tPos = ladder.position();
  var tWidth = ladder.width();
  var wWidth = $(window).width();
  set.animate({left: (wWidth / 2) - tPos.left - (tWidth / 2)}, {duration: 250, easing: 'swing', queue: true});
	centered[set.attr('id')] = ladder;
}

function moveClick(event) {
	var oldactive = $('a.active').removeClass('active');
	oldactive.siblings('form').slideUp('fast').children('input[name="word"]').blur();
	oldactive.children('img.addword').removeClass('faded');
	// Fade all ladders
	$('a.move').addClass('faded');
	// Center this ladder
	centerLadder($(this).closest('.ladder-set'), $(this).closest('.ladder-container'));
	// Un-fade this ladder
	$(this).closest('ul').find('.move').removeClass('faded');
	// Show the form
	$(this).children('img.addword').fadeOut();
	$(this).siblings('form').slideDown('fast', function () { $(this).children('input').get(2).focus(); });
	$(this).addClass('active');

  event.stopPropagation();
}

$(document).ready(function () {
	// hide all inputs when you click in empty space
  $(document.body).click(function() { $('form').slideUp('fast'); });
  
	// handle keypresses
  $('form input[name="word"]').keydown(keybdNav);
  $(document).keydown(function (e) { if (e.which == 9) { e.preventDefault(); e.stopPropagation(); } else keybdNav(e); });

  if (!done) {
    $('form').css('display', 'none').submit(handleSubmit);
    $('.move').attr('title', 'Click to add a word after this word').click(moveClick);
    
		update = $.PeriodicalUpdater(document.location.href, {
    		method: 'get',
	      data: {'lastmove': function () { return lastmove; }},
	      minTimeout: DEFAULT_POLLTIME,
	      maxTimeout: 10125,
	      multiplier: 1.5,
	      type: 'json'
			}, function(data) { handleGameJSON(data, false); }
		);

		centerLadder($('#bottom-ladder'), $('#bottom-ladder div.ladder-container:first'));
		centerLadder($('#top-ladder'), $('.ladder-container:first'));
		$('.move:first').click();
  } else {
		highlightWinningLadders(lastmove, winningchain);

		centerLadder($('#top-ladder'), $('#top-ladder a.win:first').closest('.ladder-container'));
		centerLadder($('#bottom-ladder'), $('#bottom-ladder a.win:first').closest('.ladder-container'));
		$('a.move:not(.win)').addClass('faded');
	}
});

function keybdNav (e) {
		$('li > a.active + form > input[name="word"]').removeClass('error');
		var moveKeys = {38: 'up', 40: 'down', 39: 'right', 37: 'left'};
		var active = $('a.active').closest('li');
		if (e.which in moveKeys) {
			active.siblings('form').children('input[name="word"]').blur();
			$('a.similar').removeClass('similar');
			
			var activePos = $(active).closest('ul').children('li').index($(active));
			var activeLadder = $(active).closest('.ladder-container');
			var activeLadderSet = $(activeLadder).closest('.ladder-set');
			
    	if (e.which == 38) { // up
				if ($(activeLadderSet).attr('id') == 'bottom-ladder' && activePos == 0) {
					var topCount = $(centered['top-ladder']).children('ul').children('li').length - 1;
					var newActive = $(centered['top-ladder']).children('ul').children('li').get(topCount);
					$(newActive).children('a').click();
				} else $(active).prev('li').children('a').click();
			} else if (e.which == 40) { // down
				if ($(activeLadderSet).attr('id') == 'top-ladder') {
					var topCount = $(activeLadder).children('ul').children('li').length - 1;
					if (activePos == topCount) {
						var newActive = $(centered['bottom-ladder']).children('ul').children('li').get(0);
						$(newActive).children('a').click();
					} else $(active).next('li').children('a').click();
				} else $(active).next('li').children('a').click();
			} else if (e.which == 39) { // right
				var rightLadder = $(active).closest('.ladder-container').next('.ladder-container').children('ul').get(0);
				if (rightLadder) {
					var newCount = $(rightLadder).children('li').length - 1;
					var newActive = $(rightLadder).children('li').get(Math.min(activePos, newCount));
					$(newActive).children('a').click();
				}
			} else if (e.which == 37) { // left
				var leftLadder = $(active).closest('.ladder-container').prev('.ladder-container').children('ul').get(0);
				if (leftLadder) {
					var newCount = $(leftLadder).children('li').length - 1;
					var newActive = $(leftLadder).children('li').get(Math.min(activePos, newCount));
					$(newActive).children('a').click();
				}
			}
			e.preventDefault();
			e.stopPropagation();

			active = $('a.move.active').closest('li');
			active.children('form').children('input').focus();
			var activeid = String($(active).children('a').attr('id')).replace($(active).closest('ul').attr('id') + 'm', '');
			$('a.move' + activeid + ':not(.active)').addClass('similar');
		}
}

function oc (a) {
  var o = {};
  for(var i=0;i<a.length;i++) { o[a[i]]=''; }
  return o;
}
