#include "stdafx.h"
#include"curlpost.h"
#include <codecvt>
#include <vector>
using namespace std;
Http::Http(const string& url, const map<string, string>& headers) noexcept
{
	this->url = url;
	this->headers = headers;
}

void Http::setUrl(const string& url) noexcept
{
	this->url = url;
}

void Http::setHeaders(const map<string, string>& headers) noexcept
{
	this->headers = headers;
}

std::string Http::UTF8ToGBK(const std::string& strUTF8) {
	std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
	std::wstring wTemp = cutf8.from_bytes(strUTF8);
#ifdef _MSC_VER
	std::locale loc("zh-CN");
#else
	std::locale loc("zh_CN.GB18030");
#endif
	const wchar_t* pwszNext = nullptr;
	char* pszNext = nullptr;
	mbstate_t state = {};
	std::vector<char> buff(wTemp.size() * 2);
	int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
		(loc).out(state,
			wTemp.data(), wTemp.data() + wTemp.size(), pwszNext,
			buff.data(), buff.data() + buff.size(), pszNext);
	if (std::codecvt_base::ok == res)
	{
		return std::string(buff.data(), pszNext);
	}
	return "";
}

std::string Http::GBKToUTF8(const std::string& strGBK) {
	std::vector<wchar_t> buff(strGBK.size());
#ifdef _MSC_VER
	std::locale loc("zh-CN");
#else
	std::locale loc("zh_CN.GB18030");
#endif
	wchar_t* pwszNext = nullptr;
	const char* pszNext = nullptr;
	mbstate_t state = {};
	int res = std::use_facet<std::codecvt<wchar_t, char, mbstate_t> >
		(loc).in(state,
			strGBK.data(), strGBK.data() + strGBK.size(), pszNext,
			buff.data(), buff.data() + buff.size(), pwszNext);
	if (std::codecvt_base::ok == res)
	{
		std::wstring_convert<std::codecvt_utf8<wchar_t>> cutf8;
		return cutf8.to_bytes(std::wstring(buff.data(), pwszNext));
	}
	return "";
}


string Http::escape(const std::string& POSTFIELDS) {
	CURL* curl = curl_easy_init();
	string outputstr;
	char* output1 = curl_easy_escape(curl, POSTFIELDS.c_str(), (int)POSTFIELDS.size());
	outputstr = output1;
	curl_free(output1);
	curl_easy_cleanup(curl);
	return outputstr;

}

string Http::Get() const
{
	curl_global_init(CURL_GLOBAL_ALL);
	CURL* curl = curl_easy_init();
	if (NULL == curl) {
		throw exception("curl_easy_init_error");
	}
	string my_param = "";
	struct curl_slist* chunk = NULL;
	for (auto& i : headers)
	{
		chunk = curl_slist_append(chunk, (i.first + ":" + i.second).c_str());
	}
	curl_easy_setopt(curl, CURLOPT_HTTPHEADER, chunk);
	curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &my_param);
	CURLcode res = curl_easy_perform(curl);
	if (res != CURLE_OK)
	{
		curl_slist_free_all(chunk);
		curl_easy_cleanup(curl);
		throw exception("curl_easy_perform_error");
	}
	curl_slist_free_all(chunk);
	curl_easy_cleanup(curl);
	return my_param;
}

string Http::Post(const map<string, string>& postdata) const
{
	curl_global_init(CURL_GLOBAL_ALL);
	CURL* curl = curl_easy_init();
	if (NULL == curl) {
		throw exception("curl_easy_init_error");
	}
	string my_param = "";
	curl_easy_setopt(curl, CURLOPT_URL, this->url);
	string POSTFIELDS;
	for (auto& i : postdata)
	{
		POSTFIELDS += i.first + "=" + i.second + "&";
	}
	struct curl_slist* chunk = NULL;
	for (auto& i : headers)
	{
		chunk = curl_slist_append(chunk, (i.first + ":" + i.second).c_str());
	}
	curl_easy_setopt(curl, CURLOPT_POSTFIELDS, POSTFIELDS.c_str());
	curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_data);
	curl_easy_setopt(curl, CURLOPT_WRITEDATA, &my_param);
	CURLcode res = curl_easy_perform(curl);
	if (res != CURLE_OK)
	{
		curl_slist_free_all(chunk);
		curl_easy_cleanup(curl);
		throw exception("curl_easy_perform_error");
	}
	curl_slist_free_all(chunk);
	curl_easy_cleanup(curl);
	return my_param;
}

size_t Http::write_data(void* buffer, size_t size, size_t nmemb, void* userp)
{
	(*static_cast<std::string*>(userp)).append((char*)buffer, nmemb * size);
	return nmemb * size;
}
