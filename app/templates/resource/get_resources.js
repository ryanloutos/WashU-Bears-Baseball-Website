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

/**
 * Gets the article resources for the specific category and adds the html
 */
$.get(`/resource?category=${category}&resource_type=link`, resources => {
    let thumbnail = '';
    let new_row = true;
    for (let i in resources) {
        if (new_row) {
            thumbnail += "<div class='row'>";
        }
        let description = resources[i].description ? resources[i].description : '';
        thumbnail += `
            <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                <div class="thumbnail">
                    <div class="caption">
                        <h3>${resources[i].title}</h3>
                        <p>${description}</p>
                        <p>
                            <a href="${resources[i].link}" class="btn btn-primary" role="button" target="_blank">
                                Read Article
                            </a>
                            {% if current_user.admin %}
                            <a href="/edit_resource/${resources[i].id}" class="btn btn-default" role="button">
                                Edit
                            </a>
                            {% endif %}
                        </p>
                        <p>
                            <i>
                                Uploaded: ${resources[i].timestamp}
                            </i>
                        </p>
                    </div>
                </div>
            </div>`;

        if (!new_row || i == resources.length - 1) {
            thumbnail += "</div>"
            $('#articles').append(thumbnail);
            thumbnail = '';
        }
        new_row = !new_row;
    }
});

/**
 * Gets the video resources for the specific category and adds the html
 */
$.get(`/resource?category=${category}&resource_type=video`, resources => {
    let thumbnail = '';
    let new_row = true;
    for (let i in resources) {
        if (new_row) {
            thumbnail += "<div class='row'>";
        }
        const video_id = get_youtube_video_id(resources[i].link);
        let description = resources[i].description ? resources[i].description : '';
        thumbnail += `
            <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                <div class="thumbnail">
                    <div class="caption">
                        <h3>${resources[i].title}</h3>
                        <p>${description}</p>
                        <p>
                            <iframe width="275" height="150" src="https://www.youtube-nocookie.com/embed/${video_id}" frameborder="0" 
                                    allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
                            </iframe>
                            <br>
                            <p>
                                <a href="${resources[i].link}" class="btn btn-primary" role="button" target="_blank">
                                    Link
                                </a>
                            {% if current_user.admin %}
                            <a href="/edit_resource/${resources[i].id}" class="btn btn-default" role="button">
                                Edit
                            </a>
                            {% endif %}
                        </p>
                        <p>
                            <i>
                                Uploaded: ${resources[i].timestamp}
                            </i>
                        </p>
                    </div>
                </div>
            </div>`;

        if (!new_row || i == resources.length - 1) {
            thumbnail += "</div>"
            $('#videos').append(thumbnail);
            thumbnail = '';
        }
        new_row = !new_row;
    }
});

/**
 * Gets the file resources for the specific category and adds the html
 */
$.get(`/resource?category=${category}&resource_type=file`, resources => {
    let thumbnail = '';
    let new_row = true;
    for (let i in resources) {
        if (new_row) {
            thumbnail += "<div class='row'>";
        }
        let description = resources[i].description ? resources[i].description : '';
        thumbnail += `
            <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                <div class="thumbnail">
                    <div class="caption">
                        <h3>${resources[i].title}</h3>
                        <p>${description}</p>
                        <p>
                            <p>
                                <a href="/resource/download/${resources[i].id}" class="btn btn-primary" role="button" download>
                                    Download
                                </a>
                            {% if current_user.admin %}
                            <a href="/edit_resource/${resources[i].id}" class="btn btn-default" role="button">
                                Edit
                            </a>
                            {% endif %}
                        </p>
                        <p>
                            <i>
                                Uploaded: ${resources[i].timestamp}
                            </i>
                        </p>
                    </div>
                </div>
            </div>`;

        if (!new_row || i == resources.length - 1) {
            thumbnail += "</div>"
            $('#files').append(thumbnail);
            thumbnail = '';
        }

        new_row = !new_row;
    }
});