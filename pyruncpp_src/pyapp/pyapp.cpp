// pyapp.cpp : 定义 DLL 应用程序的导出函数。
//This SDK use VS2017 and write by super1207
//2019/6/2

//软件只识别当前目录下的py*.dll文件，所以，dll文件必须这样命名，如本工程就是pyruncpp.dll ，符合插件命名规则
//dll需要使用Release-x86或者Debug-x86来编译，并且最好使用静态编译，本工程已经设置了静态编译,开发者可以直接使用

#include "stdafx.h"

//C++ stand head
#include<string>

//C++ stand using
using namespace std;

#include "./jsoncpp/json/json.h"
#include "curlpost.h"


//gobal define
#define PYEVENT(ReturnType, Name, Size) __pragma(comment(linker, "/EXPORT:" #Name "=_" #Name "@" #Size))\
extern "C" ReturnType __stdcall Name

#define PYAPI(ReturnType) extern "C" __declspec(dllexport) ReturnType __stdcall


//PYAPI的声明在pymain.lib中,PYAPI的定义在pymain.dll(软件隐藏，不对插件开发者开放)中
PYAPI(INT32)getdata(char * out);  
PYAPI(INT32)disableArg();
PYAPI(INT32)enableArg();
PYAPI(INT32)clearArg();
PYAPI(INT32)addArg(const char * in);
PYAPI(INT32)getArg(char * out);
PYAPI(INT32)seleteArg(INT32 n);
PYAPI(INT32)setTraBtnText(const char * in);
//以上所有API均出现在了下面的例子中，并且有简单说明，插件开发者可以自行体会领悟

PYAPI(const char *)runapi(const char * in,char * out); //这是一个危险的api,用于SDK开发者(非插件开发者)，插件开发者可以忽略它

//必须
PYEVENT(INT32, name, 4)(char * ret) //取插件名字事件，需要返回插件的名字，插件的名字是唯一的识别，所以不要试图返回不同的名字，另外，这个函数会在线程不安全的地方调用,所以，不要试图在这个函数中调用PYAPI，否者，可能产生死锁
{
	strncpy_s(ret, 8192, u8"RUN_CPP",8000);  //返回插件的名字，注意，必须保证返回的内容长度在8000以下(否则可能会被截断，最长不会超过8192，包括终止符在内)，并且使用utf-8编码集，SDK中所有文本均需要使用utf-8编码，以后不再单独说明
	return 0;  //这个返回0是没有实际意义的，起占位作用，下面也是，不再单独说明
}

/* 运行C++代码，输入必须为GBK,输出也是GBK*/
string static runCpp(const string& code)
{
	map<string, string> postdata =
	{
		{"code", Http::escape(code)},
		{"language","7"},
		{"fileext","cpp"}
	};
	string ret;
	try {
		ret = Http("https://tool.runoob.com/compile.php", {
			{"User - Agent","Mozilla / 5.0 (Windows NT 10.0; Win64; x64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / 64.0.3282.140 Safari / 537.36 Edge / 18.17763"},
			{"Accept - Language", "zh - CN"},
			{"Content - Type", "application / x - www - form - urlencoded; charset = UTF - 8"},
			{"Referer", "https://c.runoob.com/compile/12"},
			{"Host", "tool.runoob.com"},
			{"Origin", "https://c.runoob.com"},
			{"Connection", "Keep - Alive"},
			{"Cache - Control", "no - cache"}
			}).Post(postdata);
	}
	catch (exception& err)
	{
		return "errors:" + string(err.what());
	}
	Json::Value value;
	JSONCPP_STRING errs;
	std::unique_ptr<Json::CharReader> const jsonReader(Json::CharReaderBuilder().newCharReader());
	jsonReader->parse(ret.c_str(), ret.c_str() + ret.length(), &value, &errs);
	if (errs.empty())
	{
		Json::Value ro = value["output"];
		Json::Value re = value["errors"];
		string output, errors;
		if (ro.isString() && re.isString())
		{
			if (re.asString() != "\n" && re.asString() != "")
			{
				return "errors:" + re.asString();
			}
			else {
				return ro.asString();
			}
		}
	}
	return "errors:" + errs;

}


//必须
PYEVENT(INT32, choose, 0)() //插件被选中事件，推荐在这个函数中设置参数复选框
{
	setTraBtnText(u8"执行");   //设置翻译按钮上的文本
	clearArg();               //清除参数复选框上的数据
	disableArg();              //使参数复选框不可被选中
	addArg(u8"运行CPP");          //参数复选框增加一个"你好"
	//addArg(u8"世界");			//参数复选框增加一个"世界"
	seleteArg(0);              //选择第2个参数（下标从0开始，所以是"世界"）
	enableArg();               //使得参数复选框可以被选中
	return 0;
}

//必须
PYEVENT(INT32, mainfun,4)(char * ret)  //翻译事件，需要执行翻译过程并返回翻译结果
{
	char dat[8192];
	//char arg[8192];
	getdata(dat); //取输入框数据
	//etArg(arg);      //取参数复选框数据
	//string out = u8"数据和参数:" + string(dat) + string(arg);
	string out = runCpp(string(dat));
	if (out.length() < 8000) //返回数据的长度不能超过8000（包括字符串终止符在内）
	{
		strncpy_s(ret, 8192, out.c_str(), 8000);  //返回执行结果
	}
	else
	{
		strncpy_s(ret, 8192, u8"长度过长，无法处理", 8000);
	}
	
	return 0; 
}


