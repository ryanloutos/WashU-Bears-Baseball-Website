// these are for the default options for team and season options
var defaultTeamId = 1;
var currentSeasonId = {{ current_season.id }};

// the different selectors and/or options for the form
var teamSelector = $("#opponent");
var batterSelector = $("#batter");
var seasonSelector = $("#season");

teamSelector.change(function() {
    getBattersBasedOnTeam();
});

function getBattersBasedOnTeam() {
    let teamId = teamSelector.val();
    let apiUrl = `api/team/${teamId}/get_batters`;
    $.ajax({
        url: apiUrl,
        success: function(response) {
            if (response.status == "success") {
                batterSelector.empty();
                for (let batter of response.data) {
                    batterSelector.append(new Option(batter.name, batter.id));
                }
            }
            else {
                console.log(response);
            }
        }
    })
}

// set the default selector values
teamSelector.val(defaultTeamId);
seasonSelector.val(currentSeasonId);

getBattersBasedOnTeam();

