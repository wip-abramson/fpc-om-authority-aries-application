import React from 'react'
import DataOwnerTab from "./DataOwnerTab";
import DataScientistTab from "./DataScientistTab";

const ConnectionPage = ({connectionId}) => {

    let [dataScientistTab, setDataScientistTab] = React.useState(null)
    let [dataOwnerTab, setDataOwnerTab] = React.useState(null)



    return (<div className="connection-page">

        <h1>Congratulations, you now managed to authenticate with the OM Authority Agent. You have established a connection - {connectionId}</h1>



        <h2>Now you can generate invitations for your Data Scientist and Data Owner agents running in Juypter Notebooks</h2>
        <div>
            <button onClick={() => {
                setDataOwnerTab(false)
                setDataScientistTab(true)
            }}>Data Scientist</button>
            <button onClick={() => {
                setDataScientistTab(false)
                setDataOwnerTab(true)
            }}>Data Owner</button>
        </div>

        {dataScientistTab && <DataScientistTab connectionId={connectionId}/>}
        {dataOwnerTab && <DataOwnerTab connectionId={connectionId}/>}
    </div>)
}

export default ConnectionPage
