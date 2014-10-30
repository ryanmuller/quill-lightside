$(document).on("click", ".list.btn", function() {
  $("#list").show();
  $("#write").hide();
});

$(document).on("click", ".check.btn", function() {
  var lightbox_id = $(this).data("lightbox-id");
  $.post("/lightboxes/"+lightbox_id+"/answers",
         { "text": $(".text").val() },
         function(data) {
           console.log(data);
         });
});

$(document).on("click", ".prompt.btn", function() {
  var lightbox_id = $(this).data("lightbox-id");
  $.get("/lightboxes/"+lightbox_id, function(data) {
    $("#list").hide();
    $("#write").show();
    $(".prompt h1").text(data.prompt);
    $(".check.btn").data("lightbox-id", lightbox_id);
  });
});

$(document).ready(function() {
  $("#write").hide();
});
