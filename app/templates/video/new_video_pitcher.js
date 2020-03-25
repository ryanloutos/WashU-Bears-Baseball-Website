// these are for the default options for team and season options
var defaultTeamId = 1;
var currentSeasonId = {{ current_season.id }};

// the different selectors and/or options for the form
var teamSelector = $("#opponent");
var pitcherSelector = $("#pitcher");
var seasonSelector = $("#season");
var outingSelector = $("#outing");

// update the pitchers to choose from when you change teams
teamSelector.change(function() {
    getPitcherBasedOnTeam();
});

// update the outings when you change the pitchers
pitcherSelector.change(function() {
    getOutingsBasedOnPitcherAndSeason();
});

// update the outings when you change the season
seasonSelector.change(function() {
    getOutingsBasedOnPitcherAndSeason();
});

// AJAX request to get pitchers based on team
function getPitcherBasedOnTeam() {
    fetch(`/api/team/${teamSelector.val()}/get_pitchers`)
    .then(res => res.json())
    .then(function(response){
        if (response.status != "success"){
            console.log("Request ended in failure");
            console.log("Error: " + response.error);
        }

        pitcherSelector.empty();
        for (let pitcher of response.data) {
            pitcherSelector.append(new Option(pitcher.name, pitcher.id));
        }
        getOutingsBasedOnPitcherAndSeason();
    });
}

// AJAX request to get the correct outings
function getOutingsBasedOnPitcherAndSeason() {
    if (pitcherSelector.val() == null) {
        outingSelector.empty();
        return;
    }
    fetch(`/api/outings/season/${seasonSelector.val()}/pitcher/${pitcherSelector.val()}`)
    .then(res => res.json())
    .then(function(response) {
        if (response.status != "success") {
            console.log("Request ended in failure");
            console.log("Error: " + response.error);
        } 
        else {
            outingSelector.empty();
            outingSelector.append(new Option("", ""));
            for (let outing of response.outings) {
                outingSelector.append(new Option(outing.label, outing.id));
            }
        }
    });
}

// set the default selector values
teamSelector.val(defaultTeamId);
seasonSelector.val(currentSeasonId);

// update the pitchers on load
getPitcherBasedOnTeam();