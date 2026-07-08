unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls,
  System.Threading, System.JSON, VCLTee.TeEngine, VCLTee.Series, Vcl.ExtCtrls,
  VCLTee.TeeProcs, VCLTee.Chart, Winapi.ShellAPI, System.Net.URLClient,
  System.Net.HttpClient; // Winapi.ShellAPI entegre edildi

type
  TfrmMain = class(TForm)
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    cmbCalisanSayisi: TComboBox;
    edtMinPuan: TEdit;
    chkSadeceYatirimAlanlar: TCheckBox;
    btnAra: TButton;
    btnTaramaBaslat: TButton;
    btnAnalizGetir: TButton;
    dbgSonuclar: TDBGrid;
    mmoLoglar: TMemo;

    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;

    RestReqStats: TRESTRequest;
    RestResStats: TRESTResponse;

    procedure btnAraClick(Sender: TObject);
    procedure btnTaramaBaslatClick(Sender: TObject);
    procedure btnAnalizGetirClick(Sender: TObject);
    procedure dbgSonuclarDblClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure FormClose(Sender: TObject; var Action: TCloseAction); // Kapatma olayi eklendi
  private
    procedure GelismisAramaYap;
    procedure LogYaz(AMesaj: string);
  public
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.LogYaz(AMesaj: string);
begin
  mmoLoglar.Lines.Add(FormatDateTime('hh:nn:ss', Now) + ' [SYS] > ' + AMesaj);
end;

procedure TfrmMain.FormCreate(Sender: TObject);
var
  ProjectRoot: string;
  BackendCmd, ListenerCmd: string;
begin
  if cmbSektor.Items.Count = 0 then
  begin
    cmbSektor.Items.Add('Tümü');
    cmbSektor.Items.Add('Yazılım');
    cmbSektor.Items.Add('Otomotiv');
    cmbSektor.Items.Add('Tekstil');
  end;
  cmbSektor.ItemIndex := 0;

  if cmbCalisanSayisi.Items.Count = 0 then
  begin
    cmbCalisanSayisi.Items.Add('Tümü');
    cmbCalisanSayisi.Items.Add('1-50');
    cmbCalisanSayisi.Items.Add('50-250');
    cmbCalisanSayisi.Items.Add('250+');
  end;
  cmbCalisanSayisi.ItemIndex := 0;

  LogYaz('Sistem baslatildi. Servisler kontrol ediliyor.');

  // Proje kok dizini executable konumuna gore dinamik olarak hesaplaniyor
  ProjectRoot := ExpandFileName(ExtractFilePath(Application.ExeName) + '..\..\..\..\');

  // Servislerin baslatilma komutlari hazirlaniyor
  BackendCmd := '/c cd /d "' + ProjectRoot + 'autonomous-osint-agent\core-api" && ..\..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000';
  ListenerCmd := '/c cd /d "' + ProjectRoot + '" && .venv\Scripts\python.exe redis_listener.py';

  // Windows API kullanilarak uvicorn ve redis_listener arka planda baslatiliyor
  ShellExecute(0, 'open', 'cmd.exe', PChar(BackendCmd), nil, SW_SHOWMINIMIZED);
  ShellExecute(0, 'open', 'cmd.exe', PChar(ListenerCmd), nil, SW_SHOWMINIMIZED);

  LogYaz('Arka plan servisleri otomatik olarak tetiklendi.');
end;

procedure TfrmMain.FormClose(Sender: TObject; var Action: TCloseAction);
begin
  LogYaz('Sistem kapatiliyor, arka plan servisleri sonlandiriliyor.');
  // Uygulama kapatilirken arkada bagimli kalan Python surecleri temizleniyor
  ShellExecute(0, 'open', 'taskkill.exe', '/F /IM python.exe', nil, SW_HIDE);
end;

procedure TfrmMain.GelismisAramaYap;
begin
  LogYaz('Veritabanı sorgulaması baslatildi...');
  RestRequest.Params.Clear;
  RestRequest.Method := rmGET;
  RestRequest.Resource := 'companies';

  if Trim(edtSehir.Text) <> '' then
    RestRequest.AddParameter('sehir', Trim(edtSehir.Text), pkGETrsUnsaved);
  if (cmbSektor.ItemIndex > 0) then
    RestRequest.AddParameter('sektor', cmbSektor.Text, pkGETrsUnsaved);
  if Trim(edtMinPuan.Text) <> '' then
    RestRequest.AddParameter('min_puan', Trim(edtMinPuan.Text), pkGETrsUnsaved);

  try
    RestRequest.Execute;
    if RestResponse.StatusCode = 200 then
    begin
      MemTableSonuclar.Close;
      MemTableSonuclar.Open;
      LogYaz('Sorgu basarili: ' + IntToStr(MemTableSonuclar.RecordCount) + ' kayit listelendi.');
    end
    else
      LogYaz('Hata kuralı: HTTP API Kodu ' + RestResponse.StatusCode.ToString);
  except
    on E: Exception do LogYaz('Baglanti Hatasi: ' + E.Message);
  end;
end;

procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  GelismisAramaYap;
end;

procedure TfrmMain.btnTaramaBaslatClick(Sender: TObject);
var
  SorguKelimeleri: string;
begin
  SorguKelimeleri := Trim(cmbSektor.Text);
  if (SorguKelimeleri = '') or (cmbSektor.ItemIndex = 0) then
    SorguKelimeleri := 'Denizli Tekstil';

  LogYaz('OSINT veri toplama sureci tetikleniyor...');
  btnTaramaBaslat.Enabled := False;

  TTask.Run(procedure
  begin
    RestReqStats.Params.Clear;
    RestReqStats.Method := rmPOST;
    RestReqStats.Resource := 'companies/scan';
    RestReqStats.AddParameter('query', SorguKelimeleri, pkQUERY);

    try
      RestReqStats.Execute;
      TThread.Queue(nil, procedure
      begin
        if RestResStats.StatusCode = 202 then
          LogYaz('Islem kabul edildi: Arama botlari arkaplanda calisiyor.')
        else
          LogYaz('Hata: Tarama tetikleme islemi basarisiz oldu. Kod: ' + RestResStats.StatusCode.ToString);

        btnTaramaBaslat.Enabled := True;
      end);
    except
      on E: Exception do
      begin
        TThread.Queue(nil, procedure
        begin
          LogYaz('Sunucu baglanti hatasi: ' + E.Message);
          btnTaramaBaslat.Enabled := True;
        end);
      end;
    end;
  end);
end;

procedure TfrmMain.btnAnalizGetirClick(Sender: TObject);
var
  JSONObj: TJSONObject;
  JSONPair: TJSONPair;
  PieSeries: TPieSeries;
  i: Integer;
begin
  LogYaz('Sektorel analiz verileri sunucudan cekiliyor...');
  RestReqStats.Params.Clear;
  RestReqStats.Method := rmGET;
  RestReqStats.Resource := 'stats/industry-distribution';

  try
    RestReqStats.Execute;
    if RestResStats.StatusCode = 200 then
    begin
      chtSektor.RemoveAllSeries;
      PieSeries := TPieSeries.Create(chtSektor);
      chtSektor.AddSeries(PieSeries);

      JSONObj := TJSONObject.ParseJSONValue(RestResStats.Content) as TJSONObject;
      if Assigned(JSONObj) then
      begin
        try
          for i := 0 to JSONObj.Count - 1 do
          begin
            JSONPair := JSONObj.Pairs[i];
            PieSeries.AddPie(StrToIntDef(JSONPair.JsonValue.Value, 0), JSONPair.JsonString.Value, clTeeColor);
          end;
          LogYaz('Grafik raporu guncellendi.');
        finally
          JSONObj.Free;
        end;
      end;
    end
    else
      LogYaz('Analiz verisi sunucudan alinmadi.');
  except
    on E: Exception do LogYaz('Analiz Hatasi: ' + E.Message);
  end;
end;

procedure TfrmMain.dbgSonuclarDblClick(Sender: TObject);
var
  Detay: string;
begin
  if MemTableSonuclar.IsEmpty then Exit;

  Detay := 'Sirket Adi: ' + MemTableSonuclar.FieldByName('name').AsString + #13#10 +
           'Sektor: ' + MemTableSonuclar.FieldByName('industry').AsString + #13#10 +
           'Guven Skoru: ' + MemTableSonuclar.FieldByName('confidence_score').AsString;

  ShowMessage(Detay);
  LogYaz(MemTableSonuclar.FieldByName('name').AsString + ' sirket detaylari incelendi.');
end;

end.