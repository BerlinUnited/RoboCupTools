function PeriodicPlayer(player) 
{ 
  this.player = player;    
  this.currentStopListener = null;

  this.setPeriod = function(start,end) 
  {
    player.pause();
    if(this.currentStopListener != null) {
      this.player.media.removeEventListener("timeupdate", this.currentStopListener, false);
    }
    
    this.currentStopListener = function(event) {
        // if the user sets the current time (eg. via slider), we don't want to reset it
        // assuming that the user sets the time "obviously" different than the current interval
        if (player.node.currentTime < (start - 4.0) || player.node.currentTime > (end + 4.0)) {
            player.media.removeEventListener("timeupdate", playerGlobal.currentStopListener, false);
        } else if (player.node.currentTime > end) {
            player.setCurrentTime(start);
            player.pause();
        }
    };
    
    player.media.addEventListener("timeupdate", this.currentStopListener, false);
    player.setCurrentTime(start);
  }
}

var playerGlobal = null;
$( document ).ready(function() {
  $('#player').mediaelementplayer({
    stretching: 'responsive',
    success: function(media, node, player) {
      $('#' + node.id + '-mode').html('mode: ' + player.pluginType);
      if($('#video_configuration_source').val()) {
          player.setSrc($('#video_configuration_source').val());
      } else if($(media).children("video")[0].childElementCount <= 0) {
          player.media.createErrorMessage();
      }
      media.addEventListener('loadedmetadata', function() {
        playerGlobal = new PeriodicPlayer(player);
      });
    },
      customError: '<span class="alert alert-danger"><b>ERROR</b>: Video is not available!</span>',
    //, youtube:{ nocookie: true }
  });
});


var app = angular.module('test', ['schemaForm']);

app.controller('MainController', ['$rootScope','$scope','$http', function($rootScope, $scope, $http) {
    //
    var url = new URL(window.location.href);
    $scope.widget = { title: url.searchParams.get("name") !== null ? url.searchParams.get("name") : 'New' };
    // init log model
    $scope.logs = {};
    $scope.logs_max_duration = 0;
    $scope.zoom = "%";

    // retrieve logs
    $http.get(url.pathname + url.search + '&logs='+$scope.widget.title).then(function(response) {
        if (angular.isObject(response.data)) {
            $scope.logs = response.data;
        }
        // find the maximum log duration - needed to align all events in the timeline!
        for(var log in $scope.logs) {
            $scope.logs_max_duration = Math.max($scope.logs_max_duration, $scope.logs[log].end - $scope.logs[log].start);
        }
        // add timelines of logs
        for(var log in $scope.logs) {
            $scope.addTimeline(log);
        }
    });

    $scope.addTimeline = function(id) {
        var data = $scope.logs[id];
        // if not already available, add the label container
        if(typeof data.labels === 'undefined') { data.labels = {}; }
        if(typeof data.sync === 'undefined') { data.sync = 0.0; }
        // show the timeline and player number
        var timeline = $('<div id="'+id+'" class="timeline"><div class="info">#'+data.number+'</div></div>').css('width', $scope.zoom === '%' ? '100%' : ($scope.logs_max_duration*$scope.zoom)+'px');

        // iterate through the actions and add the interval to the timeline
        for(var interval_id in data.intervals) {
            var v = data.intervals[interval_id];
            // collect all found actions in the log file and add a control to the UI
            if($('#event_configuration input[name="'+v.type+'"]').length === 0) {
                var event_checkbox = $('<div class="col-xs-3"><div class="checkbox"><label><input type="checkbox" name="'+v.type+'" checked> '+v.type+'</label></div></div>');
                event_checkbox.change(function(e) { hide_event(e.target.name) });
                $('#event_configuration .row').append(event_checkbox);
            }
            $scope.addPeriod(timeline, interval_id);
        }
        $('#timelines').append(timeline);
    };

    $scope.addPeriod = function (timeline, interval_id) {
        var isRelative = $scope.zoom === '%';
        var model = $scope.logs[timeline.attr('id')];
        var interval = model.intervals[interval_id];
        var width = (interval.end - interval.begin)*(isRelative?(1/$scope.logs_max_duration*100):$scope.zoom);
        var starting_at = (interval.begin - model.sync)*(isRelative?(1/$scope.logs_max_duration*100):$scope.zoom);

        var o = $('<a href="#" id="' + interval_id + '" class="button ' + interval.type + '" data-toggle="tooltip" title="' + interval.type + '"></a>')
                .css("width", width + (isRelative?"%":"px"))
                .css("left", starting_at + (isRelative?"%":"px"));

        o[0].onclick = function (i, e) {
            $rootScope.$broadcast('setPeriod', $(this).parent().attr('id'), interval_id);
            o.addClass("selected");

            if ($scope.selected != null) {
                $scope.selected.removeClass("selected");
            }
            $scope.selected = o;
        };
        timeline.append(o);
    };
  
    $scope.save = function(event) {
      var name = $scope.widget.title.trim();
        if(name.length === 0 || name.toLowerCase() === 'new') {
            showSavingAlert('<b>WARNING: you need to set a tag!</b>', 'alert alert-warning', 1000, true);
            return;
        }

        var url = new URL(window.location.href);
        var game = url.searchParams.get("game");
        if (game === null) {
            showSavingAlert('<b>ERROR: invalid game id!</b>', 'alert alert-danger', 0, false);
            return;
        }

        data = [];
        for(var i in $scope.logs) {
            // check & remove empty objects/arrays
            var lbl = $scope.logs[i].labels;
            for(var l in lbl) {
                for(var a in lbl[l]) {
                    if ($.isEmptyObject(lbl[l][a])) { delete lbl[l][a]; }
                }
                if ($.isEmptyObject(lbl[l])) { delete lbl[l]; }
            }
            if ($.isEmptyObject(lbl)) { continue; }
            // add to the sending array
            data.push({'id': i, 'labels': JSON.stringify($scope.logs[i].labels, null, '  ')});
        }

        if(data.length > 0) {
          $.post(null, {"tag" : $scope.widget.title, "data" : data})
            .done(function( result ) {
              if (result === 'SUCCESS') {
                showSavingAlert('<b>Saved!</b>', 'alert alert-success', 800, true);
              } else {
                showSavingAlert('<b>'+result+'</b>', 'alert alert-danger', 0, false);
              }
            });
        } else {
          showSavingAlert('<b>Nothing to save!</b>', 'alert alert-warning', 600, true);
        }
  };

    $scope.$watch('zoom', function(newValue, oldValue) {
        // remove old timelines before adding new ones
        $("#timelines").children().remove();
        // add timelines of logs
        for(var log in $scope.logs) {
            $scope.addTimeline(log);
        }
    });
}]);

app.controller('FormController', function($scope) {
  labels = typeof ANNOTATION_LABELS === 'undefined' ? {} : ANNOTATION_LABELS;
  var properties = {};
  var form = [];
  
  for(var key in labels) {
    var p = labels[key];
    properties[key] = {
      "type": "array", 
      "title": p.title,
      "items": {"type": "string", "enum": p.labels.map(i => i.value)}
    };
    form.push({
      "key": key,
      "type": "checkboxes",
      "titleMap": p.labels
    });
  }
  
  properties["comment"] = {"type": "string", "title": "Comment"};
  form.push({
      "key": "comment",
      "type": "textarea",
      "placeholder": "Make a comment"
    });
  
  
  $scope.schema = {
    "type" : "object", 
    "properties": properties
  };
  
  $scope.form = form;

  $scope.model = {};

  $scope.$on('setPeriod', function(event, log_id, interval_id) {
      if(typeof $scope.logs[log_id].labels[interval_id] === 'undefined') { $scope.logs[log_id].labels[interval_id] = {}; }
      $scope.model = $scope.logs[log_id].labels[interval_id];
      $scope.$apply();
  });
});

app.controller('PlayerController', function($scope) {
    // add video sources to source selector
    var sourceSelect = $('#video_configuration_source');
    $('#player').children().each(function (i,s) {
        sourceSelect.append('<option value="'+this.src+'">'+(this.type?this.type:mejs.Utils.getTypeFromFile(this.src))+'</option>');
    });
    // switch source listener
    sourceSelect.change(function (e) {
        if(playerGlobal !== null) {
            window.location.hash="source="+this.options.selectedIndex;
            playerGlobal.player.setSrc(this.value);
            playerGlobal.player.setPoster('');
            playerGlobal.player.load();
        }
    });
    // set the source if available
    let location_hash = window.location.hash.substr(1).split('=');
    if(location_hash.indexOf('source') !== -1) {
        sourceSelect.val(sourceSelect.children()[location_hash[location_hash.indexOf('source') + 1]].value);
        sourceSelect.trigger( "change" );
    }
    // retrieve the video's offset
    $scope.video_offset = $('#player').data('offset');

    $scope.$on('setPeriod', function(event, log_id, interval_id) {
        if(playerGlobal !== null) {
            offset = $scope.video_offset - $scope.logs[log_id].sync;
            var t_begin = $scope.logs[log_id].intervals[interval_id].begin + offset - parseFloat($('#video_configuration_before').val());
            var t_end = $scope.logs[log_id].intervals[interval_id].end + offset + parseFloat($('#video_configuration_after').val());
            playerGlobal.setPeriod(t_begin, t_end);
        }
    });
});

app.controller('DrawingController', function($scope) {
    $scope.$on('setPeriod', function(event, log_id, interval_id) {
        //draw the robot position
        draw(
            $scope.logs[log_id].intervals[interval_id].pose.x/10.0,
            $scope.logs[log_id].intervals[interval_id].pose.y/10.0,
            $scope.logs[log_id].intervals[interval_id].pose.r,
            $scope.logs[log_id].intervals[interval_id].ball.x/10.0,
            $scope.logs[log_id].intervals[interval_id].ball.y/10.0
        );
    });
});

function hide_event(e) {
  $("."+e).toggleClass('visibility_hidden');
}

function showSavingAlert(content, clz, delay, fadeout) {
  var alert = $("#label_title_form .alert");
  alert.html(content).attr('class', clz).fadeIn();
  if (fadeout) {
    alert.delay(delay).fadeOut();
  }
}

// initialize the alert
$("#label_title_form .alert").hide();
$("#label_title_form .alert").removeClass('hidden');

// update/show the current open state of the configuration panel
$('#configuration .panel-collapse').on('show.bs.collapse', function () {
  $('#event_configuration_ctrl a[href="#'+this.id+'"] .glyphicon').toggleClass('glyphicon-plus glyphicon-minus');
}).on('hide.bs.collapse', function () {
  $('#event_configuration_ctrl a[href="#'+this.id+'"] .glyphicon').toggleClass('glyphicon-plus glyphicon-minus');
});

// show/hide configuration
$("#configuration_opener").click(function () { $("#configuration_control").fadeIn(); });
$("#configuration_closer").click(function () { $("#configuration_control").fadeOut(); });
document.addEventListener('keyup', (e) => { if(e.key === "Escape" && $("#configuration_control").is(":visible")) { $("#configuration_control").fadeOut(); }});