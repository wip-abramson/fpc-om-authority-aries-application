import React from 'react'
import {createDataOwnerInvite} from "./api/connections";

const DataOwnerTab = ({connectionId}) => {

    let [name, setName] = React.useState("")
    let [domain, setDomain] = React.useState("")
    let [invitation, setInvitation] = React.useState(null)


    function createInvitation(event) {
        event.preventDefault()
        createDataOwnerInvite(connectionId, name, domain).then(response => {
            console.log("Invitation : ", response.data.invitation)
            setInvitation(JSON.stringify(response.data.invitation))
        }).catch(error => {
            console.log("Error : ", error)
        })
    }


    return (
        <div className="panel-block">
            <div className="container">
            <h2 className="title"> Create Data Owner Invitation</h2>
                <p className="subtitle is-5">The agent that accepts this will be automatically issued a credential with the following attributes. Fill them in however you like.</p>
            <form onSubmit={createInvitation}>
                <div><label className="label">Name : </label><input className="input" value={name} onChange={(e) => setName(e.target.value)}/></div>
                <div className="control"><label className="label">Domain of Data</label><input className="input" value={domain} onChange={(e) => setDomain(e.target.value)}/></div>
                <hr/>
                <div className="control">
                    <button className="button is-primary" type="submit">Generate Invitation</button>

                </div>
            </form>

            {invitation && (
                <div className="hero">
                    <div className="hero-body">
                        <h2 className="title is-4">Data Owner Invite</h2>

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

export default DataOwnerTab
