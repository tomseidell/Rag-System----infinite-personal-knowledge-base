import { Icon } from "@iconify/react";

export function Header(){
    return(
        <div className="flex w-full justify-end">
            <div className="flex flex-row gap-5">
                <div className="flex flex-row items-center justify-center gap-1 cursor-pointer hover:bg-black/5 p-1.5 rounded-lg">
                <Icon
                    icon="solar:upload-outline"
                    width="16"
                    height="16"
                    color="dark-grey"
                />
                <h1 className="text-md">Upload</h1>
                </div>
                <div className="flex flex-row items-center justify-center gap-0.5 cursor-pointer hover:bg-black/5 p-1.5 rounded-lg">
                <Icon icon="proicons:settings" width="18" height="18" />
                <h1 className="text-md">Settings</h1>
                </div>
            </div>
        </div>
    )
}