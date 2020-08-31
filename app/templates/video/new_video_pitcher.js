// these are for the default options for team and season options
const defaultTeamId = 1;
const currentSeasonId = {{ current_season.id }};

// the different selectors and/or options for the form
const teamSelector = $("#opponent");
const pitcherSelector = $("#pitcher");
const seasonSelector = $("#season");
const outingSelector = $("#outing");
const linkInput = $("#link");
const youtubeLinkError = $("#youtube-link-error");
const submitButton = $("#submit-button");

// AJAX request to get pitchers based on team
const getPitcherBasedOnTeam = () => {
    fetch(`/api/team/${teamSelector.val()}/get_pitchers`)
        .then(res => res.json())
        .then(function (response) {
            if (response.status != "success") {
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
const getOutingsBasedOnPitcherAndSeason = () => {
    if (pitcherSelector.val() == null) {
        outingSelector.empty();
        return;
    }
    fetch(`/api/outings/season/${seasonSelector.val()}/pitcher/${pitcherSelector.val()}`)
        .then(res => res.json())
        .then(function (response) {
            if (response.status != "success") {
                console.log("Request ended in failure");
                console.log("Error: " + response.error);
            } else {
                outingSelector.empty();
                outingSelector.append(new Option("", ""));
                for (let outing of response.outings) {
                    outingSelector.append(new Option(outing.label, outing.id));
                }
            }
        });
}

// https://gist.github.com/jphase/9086823
// Returns true if the url param is a youtube video, false otherwise
const isYouTubeUrl = url => {
    const expression = /(http:|https:)?\/\/(www\.)?(youtube.com|youtu.be)\/(watch)?(\?v=)?(\S+)?/;
    const regex = new RegExp(expression);
    return url.match(regex);
};

// update the pitchers to choose from when you change teams
teamSelector.change(getPitcherBasedOnTeam);

// update the outings when you change the pitchers
pitcherSelector.change(getOutingsBasedOnPitcherAndSeason);

// update the outings when you change the season
seasonSelector.change(getOutingsBasedOnPitcherAndSeason);

// only show the Submit button when a valid YouTube link is displayed
linkInput.keyup(() => {
    if (isYouTubeUrl(linkInput.val())) {
        submitButton.css("display", "block");
        youtubeLinkError.css("display", "none");
    } else {
        submitButton.css("display", "none");
        youtubeLinkError.css("display", "block");
    }
})

// set the default selector values
teamSelector.val(defaultTeamId);
seasonSelector.val(currentSeasonId);

// update the pitchers on load
getPitcherBasedOnTeam();

// to prevent form from being submitted using "enter" or "return" key
$("form input").on("keypress", function (e) {
    return e.which !== 13;
});