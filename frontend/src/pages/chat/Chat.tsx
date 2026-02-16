import { Icon } from "@iconify/react";

export function Chat() {
  return (
    <div className="min-h-screen px-10 py-5 flex flex-col bg-[#FAF9F6]">

      {/* Header top right */}
      <div className="flex w-full justify-end">
        <div className="flex flex-row gap-5">
          <div className="flex flex-row items-center justify-center gap-1 cursor-pointer hover:bg-black/5 p-1.5 rounded-lg">
            <Icon icon="solar:upload-outline" width="16" height="16" color="dark-grey" />
            <h1 className="text-md">Upload</h1>
          </div>
          <div className="flex flex-row items-center justify-center gap-0.5 cursor-pointer hover:bg-black/5 p-1.5 rounded-lg">
            <Icon icon="proicons:settings" width="18" height="18" />
            <h1 className="text-md">Settings</h1>
          </div>
        </div>
      </div>

      {/* Chat Messages*/}
      <div className="mt-2 flex-1 flex justify-center">
        <div className="flex flex-col w-[45%] rounded-xl  content-between justify-between">
          
          <p className="text-black text-3xl mb-4">Messages</p>

          {/* Chat input */}
          <div className="flex flex-row p-3 bg-white gap-4 mx-2 mb-2 rounded-xl border border-black/10 shadow-lg hover:shadow-2xl transition-shadow duration-200">
            <input
            className="w-[95%] border-none focus:outline-none focus:ring-0 bg-white" 
            placeholder="Ask Anything...">
            </input>
            <button className="bg-black p-2 rounded-lg hover:bg-black/80 transition-colors">
                <Icon icon="material-symbols:send-outline" width="20" height="20" className="text-white"/>
            </button>

          </div>
        </div>
      </div>
    </div>
  );
}
