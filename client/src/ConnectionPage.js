import React from 'react'
import DataOwnerTab from "./DataOwnerTab";
import DataScientistTab from "./DataScientistTab";

const ConnectionPage = ({connectionId}) => {

    let [dataScientistTab, setDataScientistTab] = React.useState(true)
    let [dataOwnerTab, setDataOwnerTab] = React.useState(false)



    return (<div className="container connection-page">

        <div className="hero">
            <div className="hero-body">
                <h1 className="title is-2">Congratulations, you now managed to authenticate with the OM Authority Agent. </h1>
                <h2 className="subtitle is-3">            You have established a connection - {connectionId}</h2>
            </div>
        </div>

        <nav className="panel">
            <p className="panel-heading">
                Now you can generate invitations for your Data Scientist and Data Owner agents running in Juypter Notebooks
            </p>
            <p className="panel-tabs">
                <a className={dataScientistTab ? "is-active" : ""} onClick={() => {
                    setDataOwnerTab(false)
                    setDataScientistTab(true)
                }}>Data Scientist</a>
                <a className={dataOwnerTab ? "is-active" : ""} onClick={() => {
                    setDataScientistTab(false)
                    setDataOwnerTab(true)
                }}>Data Owner</a>
            </p>
            {dataScientistTab && <DataScientistTab connectionId={connectionId}/>}
            {dataOwnerTab && <DataOwnerTab connectionId={connectionId}/>}
        </nav>









    </div>)
}

export default ConnectionPage
