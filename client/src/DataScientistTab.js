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
        <div>
            <h2>Create Data Scientist Invitation</h2>
            <p>By accepting this invitation in the DataOwner Notebook, you will automatically be issued a credential with the following attributes. Fill them in however you like.</p>
            <form onSubmit={createInvitation}>
                <div><label>Name : </label><input value={name} onChange={(e) => setName(e.target.value)}/></div>
                <div><label>Scope of Research</label><input value={scope} onChange={(e) => setScope(e.target.value)}/></div>
                <button type="submit">Generate Invitation</button>
            </form>

            {invitation && (
                <div>
                    <h2>Data Scientist Invite</h2>
                    <h3>Copy This</h3>
                    <textarea readOnly={true} value={invitation}/>
                </div>
            )}

        </div>
    )
}

export default DataScientistTab
