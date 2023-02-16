$(function() {
    $.ajax({
        url: '/api/search'
        }).done(function (data){
            $('#business_autocomplete').autocomplete({
                source: function(request, response) {
                    var results = $.ui.autocomplete.filter(data, request.term);
                    response(results.slice(0, 10));
                },
                messages: {
                    noResults: '',
                    results: function() {
                       
            
                    }
                },
                minLength: 2,
                delay: 400
            });
        });
    });