// pymain.cpp : 定义 DLL 应用程序的导出函数。
//

#include "stdafx.h"


#include<string>   //字符串处理
#include<mutex>    //锁
#include<atomic>   //原子变量
#include<thread>   //线程
#include <chrono>  //时间

using namespace std;

#define PYEVENT(ReturnType, Name, Size) __pragma(comment(linker, "/EXPORT:" #Name "=_" #Name "@" #Size))\
extern "C" ReturnType __stdcall Name

#define PYAPI(ReturnType) extern "C" __declspec(dllexport) ReturnType __stdcall

static char dataa[8192];   //用于储存数据
static mutex runflag;  //用于保证同一时刻只有一个API调用
static atomic_int backflag = 0;  //用于判断是否返回

PYEVENT(INT32, setok, 4)(const char * dat)
{
	strncpy_s(dataa,dat,8191); //得到返回的数据
	backflag = 0;  //返回标识
	return 0;
}

PYEVENT(INT32, getcmd, 4)(char * dat)
{
	if(backflag == 1)  //表示需要向截图翻译工具发送命令
	{ 
		strncpy_s(dat, 8192, dataa, 8191);
		return 1;
	}
	return 0;
}

const char * runcmd(const char * cmd) //应用从这里获取任何想要的数据,或者执行命令
{
	runflag.lock(); //加锁以保证同一时刻只有一个API调用
	strncpy_s(dataa, cmd, 8191);//拷贝数据到全局变量
	backflag = 1;  //等于1表示正在等待数据返回
	while (backflag != 0)
	{
		this_thread::sleep_for(chrono::milliseconds(1));
	}
	return dataa;
}


PYAPI(INT32)runapi(const char * in, char * out)
{
	strncpy_s(out, 8192,runcmd(in), 8191);
	runflag.unlock();
	return 0;
}

PYAPI(INT32)getdata(char * ret)
{
	strncpy_s(ret, 8192, runcmd(R"(self.maindll.setok(str(len(str(self.inputText.get('1.0', 'end')).encode())).encode()))"), 8191);
	runflag.unlock();
	if (atoi(ret) < 8000)
	{
		strncpy_s(ret, 8192, runcmd(R"(self.maindll.setok(str(self.inputText.get('1.0', 'end')).encode()))"), 8191);
		runflag.unlock();
		return 1;
	}
	return 0;
}

PYAPI(INT32)disableArg()
{
	runcmd(u8"self.maindll.setok(str(None).encode())\nself.comboxlist['state'] = 'disabled'");
	runflag.unlock();
	return 0;
}

PYAPI(INT32)enableArg()
{
	runcmd(u8"self.maindll.setok(str(None).encode())\nself.comboxlist['state'] = 'readonly'");
	runflag.unlock();
	return 0;
}

PYAPI(INT32)clearArg()
{
	runcmd(u8"self.maindll.setok(str(None).encode())\nself.comboxlist[\"values\"] = (\"\",)\nself.comboxlist.current(0)\nself.comboxlist[\"values\"] = ()");
	runflag.unlock();
	return 0;
}

PYAPI(INT32)addArg(const char * dat)
{
	if (strlen(dat) >= 8000)
	{
		return 1;
	}
	string str = R"(self.comboxlist["values"] = self.comboxlist["values"] + (")" + string(dat) + "\", )";
	runcmd((u8"self.maindll.setok(str(None).encode())\n" + str).c_str());
	runflag.unlock();
	return 0;
}

PYAPI(INT32)getArg(char * ret)
{
	strncpy_s(ret, 8192, runcmd(R"(self.maindll.setok(str(self.comboxlist.get()).encode()))"),8191);
	runflag.unlock();
	return 0;
}

PYAPI(INT32)seleteArg(INT32 n)
{
	string str = to_string(n);
	runcmd(("self.maindll.setok(str(None).encode())\nself.comboxlist.current("+str+")").c_str());
	runflag.unlock();
	return 0;
}



PYAPI(INT32)setTraBtnText(const char * dat)
{
	if (strlen(dat) >= 8000)
	{
		return 1;
	}
	string str = dat;
	str = "\"" + str + "\"";
	runcmd((u8"self.maindll.setok(str(None).encode())\nself.translateBtn['text'] = " + str).c_str());
	runflag.unlock();
	return 0;
}



