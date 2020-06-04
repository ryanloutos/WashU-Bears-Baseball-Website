// got this function from stack overflow
const get_youtube_video_id = url => {
    let video_id = '';
    const regex = /(?:[?&]vi?=|\/embed\/|\/\d\d?\/|\/vi?\/|https?:\/\/(?:www\.)?youtu\.be\/)([^&\n?#]+)/;
    const match = url.match(regex);
    if (match && match[1].length == 11) {
        video_id = match[1];
    }
    return video_id;
};

/**
 * HTTP request for the resources for a specific category
 */
$.get(`/resource?category=${category}`, resources => {
    for (let i in resources) {
        let resource_type_div = undefined;
        let thumbnail = `
                <div class="col-xs-12 col-sm-12 col-md-6 col-lg-4">
                    <div class="thumbnail">
                        <div class="caption">
                            <h3>${resources[i].title}</h3>
                                <p>${resources[i].description}</p>`;
        if (resources[i].article_link) {
            resource_type_div = $('#articles');
            thumbnail += `
                    <p>
                        <a href="${resources[i].article_link}" class="btn btn-primary" role="button" target="_blank">Read Article</a>
                        {% if current_user.admin %}
                        <a href="#" class="btn btn-default" role="button">Edit</a>
                        {% endif %}
                    </p>`;
        }
        if (resources[i].video_link) {
            resource_type_div = $('#videos');
            const video_id = get_youtube_video_id(resources[i].video_link);
            thumbnail += `
                    <iframe width="275" height="150" src="https://www.youtube-nocookie.com/embed/${video_id}" frameborder="0" 
                        allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
                    </iframe><br>
                    <p>
                        <a href="${resources[i].video_link}" class="btn btn-primary" role="button" target="_blank">Link</a>
                        {% if current_user.admin %}
                        <a href="#" class="btn btn-default" role="button">Edit</a>
                        {% endif %}                                
                    </p>`;
        }
        if (resources[i].file_path) {
            resource_type_div = $('#files');
            thumbnail += `
                    <p>
                        <a href="/resource/download/${resources[i].id}" class="btn btn-primary" role="button" download>Download</a>
                        {% if current_user.admin %}
                        <a href="#" class="btn btn-default" role="button">Edit</a>
                        {% endif %}                                
                    </p>`;
        }
        thumbnail += `
                            <p><i>Uploaded: ${resources[i].timestamp}</i></p>
                        </div>
                    </div>
                </div>`;
        resource_type_div.append(thumbnail);
    }
});