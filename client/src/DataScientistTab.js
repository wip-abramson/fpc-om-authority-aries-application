import React from 'react'
import {createDataScientistInvite} from "./api/connections";

const DataScientistTab = ({connectionId}) => {

    let [name, setName] = React.useState("")
    let [scope, setScope] = React.useState("")
    let [invitation, setInvitation] = React.useState(null)


    function createInvitation(event) {
        event.preventDefault()

        createDataScientistInvite(connectionId, name, scope).then(response => {
            console.log("Invitation : ", response.data.invitation)
            setInvitation(JSON.stringify(response.data.invitation))
        }).catch(error => {
            console.log("Error : ", error)
        })
    }


    return (
        <div className="panel-block">
            <div className="control">
            <h2 className="title is-3">Create Data Scientist Invitation</h2>
            <p className="subtitle is-5">The agent that accepts this will be automatically issued a credential with the following attributes. Fill them in however you like.</p>
            <form onSubmit={createInvitation}>
                <div className="control"><label className="label">Organisation Name</label><input className="input" value={name} onChange={(e) => setName(e.target.value)}/></div>
                <div><label  className="label">Scope of Research</label><input className="input" value={scope} onChange={(e) => setScope(e.target.value)}/></div>
                <hr/>
                <button className="button is-submit is-primary" type="submit">Generate Invitation</button>
            </form>

            {invitation && (
                <div className="hero">
                    <div className="hero-body">
                        <h2 className="title is-4">Data Scientist Invite</h2>

                        <div className="message">
                            <h3 className="message-header">Copy This</h3>
                            <div className="message-body" >{invitation}</div>
                        </div>
                    </div>


                </div>
            )}
            </div>

        </div>
    )
}

export default DataScientistTab
