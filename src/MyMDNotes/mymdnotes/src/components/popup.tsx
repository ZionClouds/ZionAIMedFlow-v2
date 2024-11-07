import { INote } from "../App"

function Popup(props: { note: INote | null, target: string, closeModal: any, edit: any }) {
    return (
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <div class="bg-slate-50 text-black rounded shadow-lg w-[95%] md:w-3/4 h-3/4 flex flex-col overflow-clip">
                <div class='flex bg-black text-white'>
                    <div class="flex-grow"></div>
                    <div class='p-2'><button onClick={props.closeModal}>[X]</button></div>
                </div>
                {props.target === 'transcription' &&
                    <h2 class="text-xl font-bold px-2">Transcript</h2>
                }
                {props.target === 'edit' &&
                    <h2 class="text-xl font-bold px-2">Edit Medical Notes</h2>
                }

                {props.target === 'transcription' &&
                    <textarea class="w-full h-full m-2 p-2 outline-none resize-none border text-black" value={props.note?.transcription} readOnly />
                }
                {props.target === 'edit' &&
                    <textarea class="w-full h-full m-2 p-2 outline-none resize-none border text-black"
                        onInput={(e) => props.note!.updatedNotes = (e.target as HTMLTextAreaElement).value}
                        value={props.note?.updatedNotes} />
                }
                <div class="flex space-x-2">
                    {props.target === 'edit' &&
                        <button class="bg-blue-600 text-white m-2 px-4 py-2 rounded" onClick={() => props.edit(props.note)}>
                            Save
                        </button>
                    }
                    <button class="bg-slate-600 text-white m-2 px-4 py-2 rounded" onClick={props.closeModal}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}
export default Popup