$(document).ready(function()
{
  $('form').addClass('hidden');
  $('.move').attr('title', 'Click to add a word after this word')
    .click(function() {
             $('form').addClass('hidden');
             $(this).next('form').removeClass('hidden');
           });
});