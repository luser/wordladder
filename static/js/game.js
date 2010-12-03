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
    $(form).addClass('hidden');
  }
  handleGameJSON(data);
  if (!('error' in data)) {
    // focus the textbox under the word the user just played
    $('#m' + data.lastmove).click();
  }
}

function handlePlayError (form, err) {
  //TODO: network error icon or something
}

function handleGameJSON (data) {
  if ('done' in data && !done) {
    done = data.done;
		update.stop();
    //TODO: fancy this up
    document.title += " (finished)";
    $('h1').append(" (finished)");
		$('#game').after('<ul id="scores"></ul>');
		for (user in data.scores) {
			$('#scores').append('<li><img src="'+data.scores[user]['picture']+'" alt="" title="" border="0" height="32" /> '+data.scores[user]['username']+' earned '+data.scores[user]['score']+' points.</li>');
		}
  }
  var animTimer = -1;
  var numAnims = 0;
  if (data.moves.length > 0) animTimer = setInterval(redrawwires, 100);
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
	    var html =  '<ul id="l' + m.id + '" style="display:none"><li' + (m.bottom?' bottom':'') + '>';
					html += '<a id="m' + m.id + '" class="move">';
			    html += '<img src="' + picture + '" alt="' + username + '" title="' + username + '" /> ';
					html += m.word + '</a>';
					html += '<form class="hidden" method="POST" action="' + window.location + '/play">';
					html += '<input type="hidden" name="moveid" value="' + m.id + '">';
					html += '<input type="text" id="i' + m.id + '" name="word" autocomplete="off" autocorrect="off" autocapitalize="off">';
					html += '</input></form></ul>';
	    if (!m.bottom) $('#m' + m.parent).parent().append(html);
	    else $('#m' + m.parent).parent().before(html);
	    $('#m' + m.id).attr('title', 'Click to add a word after this word').click(moveClick).nextAll('form').submit(handleSubmit);
			addLink(m.id, m.parent, 'blue');
			numAnims++;
	    $('#l' + m.id).show('normal', function() {
			  numAnims--;
			  if (numAnims <= 0) {
			    clearInterval(animTimer);
			    redrawwires();
		    }
			});
	  	$('#playinfo').prepend('<span class="log">' + username + " played " + m.word + "</span>");
		}
	});
  if ('done' in data) {
    $.each(data.winningchain, function(i, mid) { $('#m' + mid).addClass('win'); });
    for (var i=0; i<data.winningchain.length-1; i++) { changeLinkColor(data.winningchain[i], data.winningchain[i+1], 'red'); }
  }
  if (data.lastmove > lastmove) lastmove = data.lastmove;
}

function moveClick(event) {
  var washidden = $(this).nextAll('form').hasClass('hidden');
  // hide all inputs first
  $('form').addClass('hidden');
  if (washidden) $(this).nextAll('form').removeClass('hidden').children('input').get(1).focus();
  else {
    // hidden now, blur it
    $(this).nextAll('form').children('input').get(1).blur();
  }

  event.stopPropagation();
}

$(document).ready(function () {
	// hide all inputs when you click in empty space
  $(document.body).click(function() { $('form').addClass('hidden'); });
  
	// hide inputs when pressing ESC
  $(document).keypress(function (e) {
		$('form input[name="word"]').removeClass('error');
    if (e.keyCode == 27) { // ESC
      $('form').addClass('hidden');
      e.preventDefault();
    }
  });

  if (!done) {
    $('form').addClass('hidden').submit(handleSubmit);
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
