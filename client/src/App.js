import React from 'react';
import logo from './logo.svg';
import './App.css';
import Invite from './Invite';
import {checkTrusted} from "./api/connections";
import ConnectionPage from './ConnectionPage'
function App() {

  let [connectionId, setConnectionId] = React.useState(null)
    let [connectionTrusted, setConnectionTrusted] = React.useState(false)

    React.useEffect(() => {

        if (connectionId && !connectionTrusted) {
            const interval = setInterval(() => {
                checkTrusted(connectionId).then(response => {
                    console.log("ACTIVE", response.data.trusted)
                    if (response.data.trusted) {
                        setConnectionTrusted(response.data.trusted)
                        return () => clearInterval(interval);
                    }

                })
            }, 2000);
            return () => clearInterval(interval);
        }


    }, [connectionId, connectionTrusted])

  return (
    <div className="App">
      <header className="App-header">
      {/*<img class="logo_text" src="logo_text.png" alt="Logo"></img>*/}
      <div class="disclaimer">Experimental</div>

          {/*<div>*/}
          <div><h2 className="title is-1">OpenMined Duet Authority</h2></div>


          {
              connectionTrusted ?

                  <ConnectionPage connectionId={connectionId}/>
                  : <>
                      <h3 className="subtitle">Scan this QrCode to make a connection and authenticate by presenting the <a href="https://indyscan.io/tx/SOVRIN_STAGINGNET/domain/188817" target="_blank">OpenMined PKI Course</a> credential</h3>
                      <Invite setConnectionId={setConnectionId}/>
                      <p className="instructions">
                          You should have received this credential by completing the Public Key Infrastructures tutorial notebooks in <a target="_blank" href="https://github.com/OpenMined/PyDentity/tree/master/tutorials/5.%20OM%20FoPC%20Course%20-%20Public%20Key%20Infrastructures">PyDentity</a>

                          <b>Make sure to set you use the mobile wallet that contains OM PKI Course credential</b>
                          <div className="hero">
                              <div className="hero-body">
                                  <h4 className="title is-3">Once you connect, you will be redirected to the appropriate page. If connection times out, try
                                      refreshing the page and try again.</h4>
                              </div>

                          </div>

                      </p>
                  </>
          }

          {/*</div>*/}
      </header>
    </div>
  );
}

export default App;
