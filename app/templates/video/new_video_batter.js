// these are for the default options for team and season options
const defaultTeamId = 1;
const currentSeasonId = {{ current_season.id }};

// the different selectors and/or options for the form
const teamSelector = $("#opponent");
const batterSelector = $("#batter");
const seasonSelector = $("#season");
const linkInput = $("#link");
const youtubeLinkError = $("#youtube-link-error");
const submitButton = $("#submit-button");

const getBattersBasedOnTeam = () => {
    let teamId = teamSelector.val();
    let apiUrl = `api/team/${teamId}/get_batters`;
    $.ajax({
        url: apiUrl,
        success: function (response) {
            if (response.status == "success") {
                batterSelector.empty();
                for (let batter of response.data) {
                    batterSelector.append(new Option(batter.name, batter.id));
                }
            } else {
                console.log(response);
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

teamSelector.change(getBattersBasedOnTeam);

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

getBattersBasedOnTeam();

// to prevent form from being submitted using "enter" or "return" key
$("form input").on("keypress", function (e) {
    return e.which !== 13;
});