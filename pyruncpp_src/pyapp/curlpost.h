#pragma once
#define CURL_STATICLIB
#include "./libcurl/curl/curl.h"
#include <string>
#include <map>
class Http {
public:
	Http(const std::string& url, const std::map<std::string, std::string>& headers = {}) noexcept;
	void setUrl(const std::string& url) noexcept;
	void setHeaders(const std::map<std::string, std::string>& headers)noexcept;
	std::string static UTF8ToGBK(const std::string& strUTF8);
	std::string static GBKToUTF8(const std::string& strGBK);
	std::string static escape(const std::string& POSTFIELDS);
	std::string Get() const;
	std::string Post(const std::map<std::string, std::string>& postdata) const;
private:
	std::string url;
	std::map<std::string, std::string> headers;
	size_t static  write_data(void* buffer, size_t size, size_t nmemb, void* userp);
};
