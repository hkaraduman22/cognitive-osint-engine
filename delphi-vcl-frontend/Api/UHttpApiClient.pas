unit UHttpApiClient;

interface

uses
  System.Classes,
  System.JSON,
  System.Net.URLClient,
  System.Net.HttpClient,
  System.Net.HttpClientComponent;

type
  THttpApiClient = class
  private
    FHttpClient: TNetHTTPClient;
    FRequest: TNetHTTPRequest;
    function BuildUrl(const APath: string): string;
    function BuildHeaders(const ABearerToken: string; AIsJsonRequest: Boolean): TNetHeaders;
  public
    constructor Create;
    destructor Destroy; override;

    function Get(const APath: string; const ABearerToken: string = ''): IHTTPResponse;
    function PostEmpty(const APath: string; const ABearerToken: string = ''): IHTTPResponse;
    function PostJson(const APath: string; const ABody: TJSONObject; const ABearerToken: string = ''): IHTTPResponse;

    property HttpClient: TNetHTTPClient read FHttpClient;
    property RequestComponent: TNetHTTPRequest read FRequest;
  end;

implementation

uses
  System.SysUtils,
  System.StrUtils,
  UApiConfig;

constructor THttpApiClient.Create;
begin
  inherited Create;

  FHttpClient := TNetHTTPClient.Create(nil);
  FHttpClient.ConnectionTimeout := 10000;
  FHttpClient.ResponseTimeout := 30000;

  FRequest := TNetHTTPRequest.Create(nil);
  FRequest.Client := FHttpClient;
end;

destructor THttpApiClient.Destroy;
begin
  FRequest.Free;
  FHttpClient.Free;
  inherited Destroy;
end;

function THttpApiClient.BuildUrl(const APath: string): string;
var
  LPath: string;
begin
  LPath := Trim(APath);
  if LPath = '' then
    raise EArgumentException.Create('Path bos olamaz.');

  if StartsText('http://', LPath) or StartsText('https://', LPath) then
    Exit(LPath);

  if LPath.StartsWith('/') then
    Result := TApiConfig.GetBaseUrl + LPath
  else
    Result := TApiConfig.GetBaseUrl + '/' + LPath;
end;

function THttpApiClient.BuildHeaders(const ABearerToken: string; AIsJsonRequest: Boolean): TNetHeaders;
var
  LCount: Integer;
  LIndex: Integer;
begin
  LCount := 1; // Accept: application/json
  if ABearerToken <> '' then
    Inc(LCount);
  if AIsJsonRequest then
    Inc(LCount);

  SetLength(Result, LCount);

  LIndex := 0;
  Result[LIndex].Name := 'Accept';
  Result[LIndex].Value := 'application/json';
  Inc(LIndex);

  if ABearerToken <> '' then
  begin
    Result[LIndex].Name := 'Authorization';
    Result[LIndex].Value := 'Bearer ' + ABearerToken;
    Inc(LIndex);
  end;

  if AIsJsonRequest then
  begin
    Result[LIndex].Name := 'Content-Type';
    Result[LIndex].Value := 'application/json; charset=utf-8';
  end;
end;

function THttpApiClient.Get(const APath: string; const ABearerToken: string): IHTTPResponse;
var
  LHeaders: TNetHeaders;
begin
  LHeaders := BuildHeaders(ABearerToken, False);
  Result := FHttpClient.Get(BuildUrl(APath), nil, LHeaders);
end;

function THttpApiClient.PostEmpty(const APath: string; const ABearerToken: string): IHTTPResponse;
var
  LHeaders: TNetHeaders;
begin
  LHeaders := BuildHeaders(ABearerToken, False);
  Result := FHttpClient.Post(BuildUrl(APath), TStream(nil), TStream(nil), LHeaders);
end;

function THttpApiClient.PostJson(const APath: string; const ABody: TJSONObject; const ABearerToken: string): IHTTPResponse;
var
  LHeaders: TNetHeaders;
  LBodyStream: TStringStream;
begin
  if not Assigned(ABody) then
    raise EArgumentNilException.Create('ABody nil olamaz.');

  LHeaders := BuildHeaders(ABearerToken, True);
  LBodyStream := TStringStream.Create(ABody.ToJSON, TEncoding.UTF8);
  try
    Result := FHttpClient.Post(BuildUrl(APath), LBodyStream, nil, LHeaders);
  finally
    LBodyStream.Free;
  end;
end;

end.
