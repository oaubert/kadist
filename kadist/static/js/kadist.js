$(document).ready( function () {
    // Tooltip for tags
    $('ul[id*="_tags"] li.blur').each(function() {
        $(this).qtip({
            content: {
                text: function(event, api) {
                          $.ajax({
                              url: '/kadist/tag/' + api.elements.target.attr('data-value').trim() + '/similar'
                          })
                              .then(function(content) {
                                  // Set the tooltip content upon successful retrieval
                                  api.set('content.text', content);
                              }, function(xhr, status, error) {
                                  // Upon failure... set the tooltip content to error
                                  api.set('content.text', status + ': ' + error);
                              });
                          return 'Loading...'; // Set some initial text
                      }
                  },
                  hide: {
                      fixed: true,
                      delay: 500
                  },
                  position: {
                      corner: {
                          target: 'rightMiddle',
                          tooltip: 'leftMiddle'
                      },
                      viewport: $(window),
                      adjust: {
                          screen: true
                      }
                  },
                  style: 'qtip-wiki'
              });
          });
});

