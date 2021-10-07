// posting function
function post() {
    let comment = $("#textarea-post").val();
    let today = new Date().toISOString();
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            comment_give: comment,
            date_give: today
        },
        success: function (response) {
            $("#modal-post").removeClass("is-active");
            window.location.reload();
        }
    })
}

// posting time 나타내기
function time2str(date) {
    let today = new Date();
    let time = (today - date) / 1000 / 60;  // 분

    if (time < 60) {
        return parseInt(time) + "분 전";
    }
    time = time / 60  // 시간
    if (time < 24) {
        return parseInt(time) + "시간 전";
    }
    time = time / 24;
    if (time < 7) {
        return parseInt(time) + "일 전";
    }
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
};

// posting card 만들기
function get_posts(username) {

    // if문 [만약 username이 아니라면?]
    if (username == undefined) {
        username = "";
    }

    $("#post-box").empty();
    $.ajax({
        type: "GET",
        url: `/get_posts?username_give=${username}`, // username의 코드를 받아오는 작업!
        data: {},
        success: function (response) {
            if (response["result"] == "success") {
                let posts = response["posts"];
                for (let i = 0; i < posts.length; i++) {
                    let post = posts[i];
                    let time_post = new Date(post["date"]);

                    // time_before로 원하는 data만 뽑아서 client에게 보여준다!
                    let time_before = time2str(time_post);


                    let html_temp = `<div class="box" id="${post["_id"]}">
                                        <article class="media">
                                            <div class="media-content">
                                                <div class="content">
                                                    <p>
                                                        <strong>${post['profile_name']}</strong><small>${time_before}</small>
                                                        <br>
                                                        ${post['comment']}
                                                    </p>
                                                </div>
                                            </div>
                                        </article>
                                    </div>`;
                    $("#post-box").append(html_temp);
                }
            }
        }
    })
}
