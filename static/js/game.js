var DEFAULT_POLLTIME = 2000;
var update = -1;
var users = {};

function handleSubmit (event) {
  var form = this;
  $.ajax({type: 'POST',
          url: document.location.href,
          data: {'lastmove': lastmove, 'word': this.word.value, 'moveid': this.moveid.value},
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
    //TODO: something more subtle, maybe fade in too
    $(form.word).addClass('error').shake(3, 4, 240);
    humanMsg.displayMsg(data.error);
  } else {
    // success
    form.word.value = '';
    $(form.word).removeClass('error');
    $(form).slideUp('fast');
  }
  handleGameJSON(data, $(form).parent().parent());
  if (!('error' in data)) {
    // focus the textbox under the word the user just played
    $('a.move' + data.lastmove).click();
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
			if (!ladder) ladder = $('a.move' + m.parent + ':last').parent().parent();
			$(ladder).children('li').each(function (i, e) {
				moveid = parseInt($(e).children('a').attr('id').replace($(ladder).attr('id') + 'm', ''));
				if (moveid > m.parent) newBranch = true;
			});

			if (newBranch) {
				newLadder = $(document.createElement('ul'));
				newLadder.attr('id', 'l' + m.id);
				$(ladder).children('li').each(function (i, e) {
					moveid = parseInt($(e).children('a').attr('id').replace($(ladder).attr('id') + 'm', ''));
					if (moveid <= m.parent) {
						newMove = $(e).clone();
						newMove.children('a').attr('id', newLadder.attr('id') + 'm' + moveid);
						newMove.children('a').click(moveClick).nextAll('form').submit(handleSubmit);
						newMove.css('opacity', '0.5').hover(function () { $(this).css('opacity', 1); }, function () { $(this).css('opacity', '0.5'); });
						newMove.appendTo(newLadder);
					}
				});
			} else newLadder = $(ladder);

			// Add the new move.
	    var html =  '<li' + (m.bottom?' bottom':'') + '>';
					html += '<a id="' + newLadder.attr('id') + 'm' + m.id + '" class="move move' + m.id + '">';
			    html += '<img src="' + picture + '" alt="' + username + '" title="' + username + '" /> ';
					html += m.word + '</a>';
					html += '<form method="POST" action="' + window.location + '/play">';
					html += '<input type="hidden" name="moveid" value="' + m.id + '">';
					html += '<input type="hidden" name="ladderid" value="' + newLadder.attr('id') + '">';
					html += '<input type="text" id="' + newLadder.attr('id') + 'i' + m.id + '" name="word" autocomplete="off" autocorrect="off" autocapitalize="off">';
					html += '</input></form></li>';
			
			if (m.bottom) newLadder.prepend(html);
			else newLadder.append(html);			

			// Put the new ladder next to the old one.
			if (newBranch) {
				var newContainer = $(document.createElement('div')).addClass('ladder-container').hide().css('opacity', 0);
				var newProp = $(document.createElement('div')).addClass('ladder-width');
				$(newContainer).append(newProp).append(newLadder);
				$(ladder).parent().after(newContainer);
				$(newContainer).animate({width: 'show'}, {duration: 500, queue: true});
				$(newContainer).animate({opacity: 1}, {duration: 500, queue: true});
			}

			// Hide the old form.
			$('form').slideUp('fast');

			// Set up handlers for new move.
	    $('#' + newLadder.attr('id') + 'm' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).nextAll('form').submit(handleSubmit).hide();
		}
	});
  if ('done' in data) $.each(data.winningchain, function(i, mid) { $('#m' + mid).addClass('win'); });
  if (data.lastmove > lastmove) lastmove = data.lastmove;
}

function moveClick(event) {
	var washidden = $(this).nextAll('form').css('display') == 'none';
  // Hide all inputs first
  $('form').slideUp('fast');
	// Fade all ladders
	$('.ladder-container').animate({opacity: 0.5}, 100);
	// Center this ladder
	var lSet = $(this).closest('.ladder-set');
	var tCon = $(this).closest('.ladder-container');
	var tPos = tCon.position();
	var tWidth = tCon.width();
	var wWidth = $(window).width();
	lSet.animate({left: (wWidth / 2) - tPos.left - (tWidth / 2)}, 250);
	// Un-fade this ladder
	$(this).parent().parent().parent().animate({opacity: 1}, 100);
	// Show the form
  if (washidden) $(this).nextAll('form').slideDown('fast', function () { $(this).children('input').get(2).focus(); });
  else {
    // Hidden now, blur it
    $(this).nextAll('form').children('input').get(2).blur();
  }

  event.stopPropagation();
}

$(document).ready(function () {
	// hide all inputs when you click in empty space
  $(document.body).click(function() { $('form').slideUp('fast'); });
  
	// hide inputs when pressing ESC
  $(document).keypress(function (e) {
		$('form input[name="word"]').removeClass('error');
    if (e.keyCode == 27) { // ESC
      $('form').slideUp('fast');
      e.preventDefault();
    }
  });

  if (!done) {
    $('form').css('display', 'none').submit(handleSubmit);
    $('.move').attr('title', 'Click to add a word after this word').click(moveClick);
    
		update = $.PeriodicalUpdater(document.location.href, {
    		method: 'get',
	      data: {'lastmove': function () { return lastmove; }},
	      minTimeout: DEFAULT_POLLTIME,
	      maxTimeout: 10125,
	      multiplier: 1.5,
	      type: 'json',
			}, function(data) { handleGameJSON(data); }
		);
  }
});
