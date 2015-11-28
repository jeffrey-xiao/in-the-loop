var loopApp = angular.module('loopApp', ["firebase", 'ngRoute', 'chart.js']);
var stop = false;
mapLoaded = false;
loopApp.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
  when('/', {
    templateUrl: 'templates/home.html',
    controller: 'HomeController'
  }).
  when('/article/:id', {
    templateUrl: 'templates/article.html',
    controller: 'ArticleController'
  }).
  otherwise({
    redirectTo: '/'
  });
}]).run(function($rootScope, $location) {
  $rootScope.$on( "$routeChangeStart", function(event, next, current) {
    stop = false;
    $('#loader').show().removeClass('done');
    loaderAnimation();
  });
});
function initMap(){
  mapLoaded = true;
}
loopApp.controller('HomeController', ['$scope', '$firebaseArray', function($scope, $firebaseArray) {
  $(window).scrollTop(0);
  setTimeout(function(){
    new WOW().init();
  },1);
  var ref = new Firebase("https://in-the-loop.firebaseio.com/");
  $scope.articles = $firebaseArray(ref);
  $scope.articles.$loaded().then(function(){
    var loaded = 0;
    var complete = false;
    var total = $scope.articles.length;
    function done(){
      if(!complete){
        complete = true;
        $('#loader').hide();
        stop = true;
      }
    }
    for(var i = 0; i < total; i++){
      $('<img src="img/uploads/'+$scope.articles[i].image+'" />').load(function(){
        loaded++;
        if(loaded == total){ done(); }
      });
    }
    setTimeout(function(){
      done();
    }, 5000);
  });
}]);

loopApp.controller('ArticleController', ['$scope', '$firebaseObject', '$routeParams', function($scope, $firebaseObject, $routeParams) {
  $(window).scrollTop(0);
  setTimeout(function(){
    new WOW().init();
  },1);
  $scope.labels = ['Libertarian', 'Liberal', 'Green', 'Conservative'];
  $scope.chart = [0,0,0,0];
  $scope.chartColours = ["#FF7300","#DE2121","#15CF21","#1966D1"];
  var locs = [];
  function queueLocs(){
    if(mapLoaded){
      for(var i = 0; i < locs.length; i++){
        var map = new google.maps.Map($('.map-embed')[i], {
          zoom: 4,
          center: {lat:locs[i].lat, lng: locs[i].lon},
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });

        var marker = new google.maps.Marker({
          position: {lat:locs[i].lat, lng: locs[i].lon},
          map: map
        });
      }
    }else{
      setTimeout(queueLocs, 500);
    }
  }
  var ref = new Firebase("https://in-the-loop.firebaseio.com/"+$routeParams.id);
  $scope.article = $firebaseObject(ref);
  $scope.article.$loaded().then(function(){
    var chart = $scope.article['political-sum'];
    sum = chart['Libertarian'] + chart['Liberal'] + chart['Green'] + chart['Conservative'];
    $scope.chart[0] = Math.round(chart['Libertarian'] / sum * 100);
    $scope.chart[1] = Math.round(chart['Liberal'] / sum * 100);
    $scope.chart[2] = Math.round(chart['Green'] / sum * 100);
    $scope.chart[3] = Math.round(chart['Conservative'] / sum * 100);
    if(!$scope.article.locations){
      $scope.article.locations = [];
    }
    for(var i = 0; i < $scope.article.locations.length; i++){
      locs.push({lat:$scope.article.locations[i].lat, lon:$scope.article.locations[i].lon});
    }
    for(var i = 0; i < $scope.article.data.length; i++){
      var url = $scope.article.data[i].source.url;
      url = url.replace('http://', '');
      url = url.replace('https://', '');
      url = url.replace('www.', '');
      url = url.replace('.co.', '.');
      url = url.substring(0, url.indexOf('/'));
      url = url.substring(0, url.lastIndexOf('.'));
      url = url.substring(url.lastIndexOf('.')+1);
      if(!$scope.article.data[i].date){
        $scope.article.data[i].date = 'N/A';
      }else{
        $scope.article.data[i].date = $scope.article.data[i].date.substring(0, $scope.article.data[i].date.indexOf('T'));
      }

      $scope.article.data[i].source.name = url.toUpperCase();
      if($scope.article.data[i].type=='paragraph'){
        $scope.article.data[i].sentiment = Object.keys($scope.article.data[i]['political-sentiment']).reduce(function(a, b){ return $scope.article.data[i]['political-sentiment'][a] > $scope.article.data[i]['political-sentiment'][b] ? a : b });
      }
    }
    $('#loader').hide();
    stop = true;
    setTimeout(queueLocs, 1);
  });
}]);


function loaderAnimation(){
  var canvas = $('#loader-canvas')[0];
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  var ctx = canvas.getContext("2d");

  var TAU = 2 * Math.PI;

  times = [];
  function loop() {
    if(stop) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    update();
    draw();
    requestAnimationFrame(loop);
  }

  function Ball (startX, startY, startVelX, startVelY) {
    this.x = startX || Math.random() * canvas.width;
    this.y = startY || Math.random() * canvas.height;
    this.vel = {
      x: startVelX || Math.random() * 2 - 1,
      y: startVelY || Math.random() * 2 - 1
    };
    this.update = function(canvas) {
      if (this.x > canvas.width + 50 || this.x < -50) {
        this.vel.x = -this.vel.x;
      }
      if (this.y > canvas.height + 50 || this.y < -50) {
        this.vel.y = -this.vel.y;
      }
      this.x += this.vel.x;
      this.y += this.vel.y;
    };
    this.draw = function(ctx, can) {
      ctx.beginPath();
      ctx.globalAlpha = .4;
      ctx.fillStyle = '#cccccc';
      ctx.arc((0.5 + this.x) | 0, (0.5 + this.y) | 0, 3, 0, TAU, false);
      ctx.fill();
    }
  }

  var balls = [];
  for (var i = 0; i < canvas.width * canvas.height / (100*100); i++) {
    balls.push(new Ball(Math.random() * canvas.width, Math.random() * canvas.height));
  }

  var lastTime = Date.now();
  function update() {
    var diff = Date.now() - lastTime;
    for (var frame = 0; frame * 16.6667 < diff; frame++) {
      for (var index = 0; index < balls.length; index++) {
        balls[index].update(canvas);
      }
    }
    lastTime = Date.now();
  }
  var mouseX = -1e9, mouseY = -1e9;
  document.addEventListener('mousemove', function(event) {
    mouseX = event.clientX;
    mouseY = event.clientY;
  });

  function distMouse(ball) {
    return Math.hypot(ball.x - mouseX, ball.y - mouseY);
  }

  function draw() {
    ctx.globalAlpha=1;
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0,0,canvas.width, canvas.height);
    for (var index = 0; index < balls.length; index++) {
      var ball = balls[index];
      ball.draw(ctx, canvas);
      ctx.beginPath();
      for (var index2 = balls.length - 1; index2 > index; index2 += -1) {
        var ball2 = balls[index2];
        var dist = Math.hypot(ball.x - ball2.x, ball.y - ball2.y);
        if (dist < 100) {
          ctx.strokeStyle = "#dddddd";
          ctx.globalAlpha = 1 - (dist > 100 ? .8 : dist / 150);
          ctx.lineWidth = "2px";
          ctx.moveTo((0.5 + ball.x) | 0, (0.5 + ball.y) | 0);
          ctx.lineTo((0.5 + ball2.x) | 0, (0.5 + ball2.y) | 0);
        }
      }
      ctx.stroke();
    }
  }

  // Start
  loop();
}
$(function(){
  $('body').on('click', '.fullImage', function(){
    $(this).toggleClass('full');
    if($(this).hasClass('full')){
      var maxScale = Math.min(($(window).width()-30)/$(this).width(), ($(window).height()-30 - $('#navbar').outerHeight())/$(this).height());
      var centerY = $(this).offset().top + $(this).outerHeight()/2;
      var centerX = $(this).offset().left + $(this).outerWidth()/2;
      var halfWidth = $(this).outerWidth()/2*maxScale;
      var halfHeight = $(this).outerHeight()/2*maxScale;
      var top = centerY - halfHeight;
      var left = centerX - halfWidth;
      console.log('scale('+maxScale+'), translate('+(15-left)+'px,'+(15-top)+'px)');
      $(this).css('transform', 'scale('+maxScale+') translate('+(15-left)+'px,'+(15-top+$('#navbar').outerHeight())+'px)');
    }else{
      $(this).css('transform', '');
    }
  });
});
