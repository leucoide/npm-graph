

React = require('react')
$ = require('zepto-browserify').$

var App = React.createClass({
  getInitialState: function() {
    setInterval(this.getJobLIst,2000);
    return {jobs:{}};
  },
  getJobLIst:function(){

    $.ajax({
      url:"/jobs",
      type:"GET",
      dataType:"json",
      success:function(data){
        var i = 0;
        for(;i<data.length;i++){
          this.updateJob(data[i]);
        }
        // this.setState({jobs:data});
      }.bind(this),
      error:function(xhr,status,error){
        // text = xhr.ResponseText;
        console.log(xhr.response);
        // console.log(JSON.parse(text));
      }
    });

  },
  updateJob:function(jobId){
    var url = "job/"+jobId;
    $.ajax({
      url:url,
      type:"GET",
      dataType:"json",
      success:function(data){
        var state = this.state;
        state.jobs[jobId] = data;

        this.setState(state);
      }.bind(this),
      error:function(xhr,status,error){
        // text = xhr.ResponseText;
        console.log(xhr.response);
        // console.log(JSON.parse(text));
      }
    });
  },
  render: function() {
    return (
      <div>
        <JobSubmit url="/crawl"/>
        <JobList jobs={this.state.jobs}/>
      </div>
    );
  }
});

var JobSubmit = React.createClass({
  getInitialState: function() {
    return {data:{}};
  },
  render: function(){
    return(
      <div>
        <form onSubmit={this.handleSubmit}>
          <input type="text" ref="from" />
          <input type="text" ref="to" />
          <input type="submit" value="send" />
        </form>
      </div>
    )
  },
  handleSubmit:function(e){
    e.preventDefault();
    var commandData = {"from":+this.refs.from.getDOMNode().value.trim(),
                       "to":+this.refs.to.getDOMNode().value.trim()};
    console.log(commandData);
    this.setState({data:commandData});
    $.ajax({
      url:this.props.url,
      dataType:"json",
      contentType:"application/json; charset=utf-8",
      type:"POST",
      data:JSON.stringify(commandData),
      success:function(data){},
      error:function(xhr,status,error){
        // text = xhr.ResponseText;
        console.log(xhr.response);
        // console.log(JSON.parse(text));
        }
    });

  }

});

var JobList = React.createClass({
  renderJob:function(jobId){
    var jobInfo = this.props.jobs[jobId];

    return(
      <JobDisplay key = {jobId} jobId={jobId} jobInfo={jobInfo}/>
    )
  },
  render:function(){
    // console.log(this.props.jobs);
    var jobs = Object.keys(this.props.jobs).map(this.renderJob);
    return(
      <div>
        {jobs}
      </div>
    )
  }
});
var JobDisplay = React.createClass({

  render:function(){
    var timeToFinish = ((+this.props.jobInfo.total) - (+this.props.jobInfo.current))*(+this.props.jobInfo.meanStepTime)

    return(
      <div>
      <div>JOB {this.props.jobId} ::from {this.props.jobInfo.startPoint} to {this.props.jobInfo.endPoint}:: </div>
      <div>{this.props.jobInfo.current} of {this.props.jobInfo.total}</div>
      <div>{timeToFinish} seconds remeaning</div>
      <div>---------------------------------------------</div>

      </div>
    )
  }
});


React.render(
  <App />,
  document.getElementById('app')
);
