const batterId = {{ batter.id }}
let seasonId = {{ current_season.id }}

// got this function from stack overflow
/**
 * Gets the youtube video id from the youtube link
 * @param {String} url the youtube video url
 */
const get_youtube_video_id = url => {
    const regex = /(?:[?&]vi?=|\/embed\/|\/\d\d?\/|\/vi?\/|https?:\/\/(?:www\.)?youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    if (match && match[1].length == 11) {
        return match[1];
    }
    return;
};

const updateVideos = () => {
    seasonId = $('#season-selector').val()
    $.get(`/videos/batter/${batterId}/season/${seasonId}`, videos => {
        $('#all-videos').empty();
        let thumbnail = '';
        let new_row = true;
        for (let i in videos) {
            if (new_row) thumbnail += "<div class='row'>";
            const video_id = get_youtube_video_id(videos[i].link);
            thumbnail += `
                <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                    <div class="thumbnail">
                        <div class="caption">
                            <h3>${videos[i].title}</h3>
                            <p>
                                <iframe width="275" height="150" src="https://www.youtube-nocookie.com/embed/${video_id}" frameborder="0" 
                                        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
                                </iframe>
                                <br>
                                <p>
                                    <a href="${videos[i].link}" class="btn btn-primary" role="button" target="_blank">
                                        Link
                                    </a>
                                    {% if current_user.admin %}
                                    <a href="/edit_video_batter/${videos[i].id}" class="btn btn-default" role="button">
                                        Edit
                                    </a>
                                {% endif %}
                            </p>
                            <p>
                                <i>
                                    ${videos[i].date}
                                </i>
                            </p>
                        </div>
                    </div>
                </div>`;

            if (!new_row || i == videos.length - 1) {
                thumbnail += "</div>"
                $('#all-videos').append(thumbnail);
                thumbnail = '';
            }
            new_row = !new_row;
        }
    });
}

updateVideos();
$('#season-selector').on('change', updateVideos)
