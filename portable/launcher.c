// Small Windows GUI bootstrap. The application and its interpreter stay together.
#define UNICODE
#define _UNICODE
#include <windows.h>
#include <wchar.h>
#include <stdio.h>

static int fail(const wchar_t *message) {
    wchar_t path[32768], dir[32000];
    if (GetEnvironmentVariableW(L"LOCALAPPDATA", dir, 31960) > 0) {
        wcscat(dir, L"\\ZhixuAI");
        CreateDirectoryW(dir, NULL);
        swprintf(path, 32768, L"%ls\\launcher.log", dir);
        FILE *file = _wfopen(path, L"a, ccs=UTF-8");
        if (file) { fwprintf(file, L"%ls\n", message); fclose(file); }
    }
    MessageBoxW(NULL, message, L"知序 AI · 无法启动", MB_OK | MB_ICONERROR);
    return 1;
}

int WINAPI WinMain(HINSTANCE h, HINSTANCE prev, LPSTR cmd, int show) {
    static wchar_t root[32768], exe[32768], args[32768];
    DWORD size = GetModuleFileNameW(NULL, root, 32768);
    if (!size || size >= 15000) return fail(L"请将软件完整解压到较短的目录。");
    *wcsrchr(root,L'\\') = L'\0';
    swprintf(exe,32768,L"%ls\\runtime\\python.exe",root);
    swprintf(args,32768,L"\"%ls\" -I -B \"%ls\\app\\portable.py\"",exe,root);
    STARTUPINFOW si = {0}; si.cb = sizeof(si);
    PROCESS_INFORMATION pi = {0};
    if (!CreateProcessW(exe,args,NULL,NULL,FALSE,CREATE_NO_WINDOW,NULL,root,&si,&pi))
        return fail(L"未能启动内置运行环境。请重新完整解压 ZIP，再双击 知序AI.exe。诊断日志位于 %LOCALAPPDATA%\\ZhixuAI。");
    CloseHandle(pi.hThread);
    WaitForSingleObject(pi.hProcess, INFINITE);
    DWORD code=1; GetExitCodeProcess(pi.hProcess,&code); CloseHandle(pi.hProcess);
    if (code != 0) return fail(L"启动失败。请完整解压软件，并确认用户文件夹可写。详情见 %LOCALAPPDATA%\\ZhixuAI 中的日志。");
    return 0;
}
