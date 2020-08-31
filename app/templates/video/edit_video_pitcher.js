// these are for the default options for team and season options
const defaultTeamId = 1;
const currentSeasonId = {{ current_season.id }};
const prevOutingId = '{{ video.outing_id }}';
const prevPitcherId = {{ video.pitcher_id }};

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
    $.get(`/api/team/${teamSelector.val()}/get_pitchers`, response => {
        if (response.status != "success") {
            console.log("Request ended in failure");
            console.log("Error: " + response.error);
        }
        pitcherSelector.empty();
        for (let pitcher of response.data) {
            if (pitcher.id == prevPitcherId) {
                pitcherSelector.append(new Option(pitcher.name, pitcher.id, true, true));
            } else {
                pitcherSelector.append(new Option(pitcher.name, pitcher.id));
            }
        }
        getOutingsBasedOnPitcherAndSeason();
    })
}

// AJAX request to get the correct outings
const getOutingsBasedOnPitcherAndSeason = () => {
    if (pitcherSelector.val() == null) {
        outingSelector.empty();
        return;
    }
    $.get(`/api/outings/season/${seasonSelector.val()}/pitcher/${pitcherSelector.val()}`, response => {
        if (response.status != "success") {
            console.log("Request ended in failure");
            console.log("Error: " + response.error);
        } else {
            outingSelector.empty();
            outingSelector.append(new Option("", ""));
            for (let outing of response.outings) {
                if (outing.id == prevOutingId) {
                    outingSelector.append(new Option(outing.label, outing.id, true, true));
                } else {
                    outingSelector.append(new Option(outing.label, outing.id));
                }
            }
        }
    })
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

// run initially to get the pitchers for the team
getPitcherBasedOnTeam();

// to prevent form from being submitted using "enter" or "return" key
$("form input").on("keypress", function (e) {
    return e.which !== 13;
});