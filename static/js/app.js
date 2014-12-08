var checkInterv;
var answerId;

$(document).on("click", ".list.btn", function() {
  $("#list").show();
  $("#write").hide();
});

$(document).on("click", ".check.btn", function() {
  var lightbox_id = $(this).data("lightbox-id");
  $(".result span").text("Loading...");
  $.post(
    "/lightboxes/"+lightbox_id+"/answers",
    { "text": $(".text").val() },
    function(data) {
      clearInterval(checkInterv);
      answerId = data.answer_id;
      checkInterv = window.setInterval(function() {
        $.get("/answers/"+answerId+"/result", function(data) {
          if(data.hasOwnProperty("label")) {
            clearInterval(checkInterv);

            if (data.label === "0" || data.label === "1") {
              $(".result span").text("Hmm... try answering differently.");
            } else if (data.label === "2" || data.label === "3") {
              $(".result span").text("Good start! Try explaining your answer further.");
            } else if (data.label === "5") {
              $(".result span").text("Awesome answer!");
            }
          }
        });
      }, 500);
    });
});

$(document).on("click", ".prompt.btn", function() {
  var lightbox_id = $(this).data("lightbox-id");
  $.get("/lightboxes/"+lightbox_id, function(data) {
    $("#list").hide();
    $("#write").show();
    $("#write .prompt h1").text(data.prompt);
    $("#write .text").val("");
    $("#write .result span").text("");
    $("#write .check.btn").data("lightbox-id", lightbox_id);
  });
});

$(document).ready(function() {
  $("#write").hide();
});
